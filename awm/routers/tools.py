import base64
import os
import yaml
import logging
from typing import Tuple, Union
from fastapi import APIRouter, Query, Depends, Request, Response
from awm.authorization import authenticate
from awm.models.tool import ToolInfo
from awm.models.page import PageOfTools
from awm.models.error import Error
from awm.utils.node_registry import EOSCNodeRegistry
from awm.utils.repository import Repository


AWM_TOOLS_REPO = os.getenv("DB_URL", "https://github.com/grycap/tosca/blob/eosc_lot1/templates/")
router = APIRouter()
logger = logging.getLogger(__name__)


def _get_tool_type(tosca: dict) -> str:
    try:
        node_templates = tosca.get('topology_template', {}).get('node_templates', {})
        for _, node in node_templates.items():
            if node.get('type', '') == 'tosca.nodes.Container.Application.Docker':
                return "container"
    except Exception:
        logger.exception("Error getting tool type using default 'vm'")
    return "vm"


def _get_tool_info_from_repo(elem: str, path: str, version: str, request: Request) -> ToolInfo:
    tosca = yaml.safe_load(elem)
    metadata = tosca.get("metadata", {})
    tool_id = path.replace("/", "_")
    url = str(request.url_for("get_tool", tool_id=tool_id))
    if version and version != "latest":
        url += "?version=%s" % version
    tool = ToolInfo(
        id=tool_id,
        self_=url,
        version='latest',
        type=_get_tool_type(tosca),
        name=metadata.get("template_name", ""),
        description=tosca.get("description", ""),
        blueprint=elem,
        blueprintType="tosca"
    )
    if metadata.get("template_author"):
        tool.authorName = metadata.get("template_author")
    if version:
        tool.version = version
    return tool


def get_tool_from_repo(tool_id: str, version: str, request: Request) -> Tuple[Union[ToolInfo, Error], int]:
    # tool_id was provided with underscores; convert back path
    repo_tool_id = tool_id.replace("_", "/")
    try:
        repo = Repository.create(AWM_TOOLS_REPO)
        if version:
            response = repo.get_by_sha(version)
        else:
            response = repo.get_by_path(repo_tool_id, True)
    except Exception as e:
        logger.error("Failed to get tool info: %s", e)
        msg = Error(id="503", description="Failed to get tool info")
        return msg, 503

    if response.status_code == 404:
        msg = Error(id="404", description="Tool not found")
        return msg, 404
    if response.status_code != 200:
        logger.error("Failed to fetch tool: %s", response.text)
        msg = Error(id="503", description="Failed to fetch tool")
        return msg, 503

    template = base64.b64decode(response.json().get("content").encode()).decode()
    if not version or version == "latest":
        version = response.json().get("sha")

    tool = _get_tool_info_from_repo(template, repo_tool_id, version, request)
    return tool, 200


# GET /tools
@router.get("/tools",
            summary="List all tool blueprints",
            responses={200: {"model": PageOfTools,
                             "description": "Success"},
                       400: {"model": Error,
                             "description": "Invalid parameters or configuration"},
                       401: {"model": Error,
                             "description": "Permission denied"},
                       403: {"model": Error,
                             "description": "Forbidden"},
                       419: {"model": Error,
                             "description": "Re-delegate credentials"},
                       503: {"model": Error,
                             "description": "Try again later"}})
def list_tools(
    request: Request,
    from_: int = Query(0, alias="from", ge=0,
                       description="Index of the first element to return"),
    limit: int = Query(100, alias="limit", ge=1,
                       description="Maximum number of elements to return"),
    all_nodes: bool = Query(False, alias="allNodes"),
    user_info=Depends(authenticate)
):

    tools = []
    try:
        repo = Repository.create(AWM_TOOLS_REPO)
        tools_list = repo.list()
    except Exception as e:
        logger.error("Failed to get list of Tools: %s", e)
        msg = Error(description="Failed to get list of Tools")
        return Response(msg.model_dump_json(exclude_unset=True), 503, mimetype="application/json")

    count = 0
    for _, elem in tools_list.items():
        count += 1
        if from_ > count - 1:
            continue
        try:
            tool = _get_tool_info_from_repo(repo.get(elem), elem['path'], elem['sha'], request)
            tools.append(tool)
            if len(tools) >= limit:
                break
        except Exception as ex:
            logger.error("Failed to get tool info: %s", ex)

    remote_count = 0
    if all_nodes:
        remote_count, remote_tools = EOSCNodeRegistry.list_tools(from_, limit, count, user_info)
        tools.extend(remote_tools)

    page = PageOfTools(from_=from_, limit=limit, elements=tools, count=len(tools_list) + remote_count)
    page.set_next_and_prev_pages(request, all_nodes)
    return Response(content=page.model_dump_json(exclude_unset=True, by_alias=True), status_code=200,
                    media_type="application/json")


# GET /tool/{tool_id}
@router.get("/tool/{tool_id}",
            summary="Get information about a tool blueprint",
            responses={200: {"model": ToolInfo,
                             "description": "Accepted"},
                       400: {"model": Error,
                             "description": "Invalid parameters or configuration"},
                       401: {"model": Error,
                             "description": "Permission denied"},
                       403: {"model": Error,
                             "description": "Forbidden"},
                       404: {"model": Error,
                             "description": "Not found"},
                       419: {"model": Error,
                             "description": "Re-delegate credentials"},
                       503: {"model": Error,
                             "description": "Try again later"}})
def get_tool(tool_id: str,
             request: Request,
             version: str = Query("latest", description="If missing, the latest version will be returned"),
             user_info=Depends(authenticate)):
    """Get information about an existing tool blueprint

    :rtype: ToolInfo
    """
    tool_or_msg, status_code = get_tool_from_repo(tool_id, version, request)

    return Response(content=tool_or_msg.model_dump_json(exclude_unset=True, by_alias=True),
                    status_code=status_code, media_type="application/json")
