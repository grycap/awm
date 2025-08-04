import os
import logging
import requests
from fastapi import APIRouter, Query, Depends, Request, Response
from awm.authorization import authenticate
from awm.models.tool import ToolInfo
from awm.models.page import PageOfTools
from awm.models.error import Error


router = APIRouter()
TOOLS_MARKET_URL = os.getenv("TOOLS_MARKET_URL", "https://api.eosc.athenarc.gr")
logger = logging.getLogger(__name__)


# GET /
@router.get("/",
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

    response = requests.get(TOOLS_MARKET_URL + "/tools/api/v1?pageSize=%s&from=%s" % (limit, from_),
                            headers={"Authorization": "Bearer %s" % user_info['token']},
                            timeout=10)
    if response.status_code != 200:
        logger.error("Failed to fetch tools from market: %s", response.text)
        msg = Error(description="Failed to fetch tools from market")
        return Response(content=msg.model_dump_json(), status_code=503, media_type="application/json")

    tools_info = response.json()

    tools = []
    for tool_info in tools_info.get("content"):
        pid = tool_info.get("pid").replace("/", "_")
        url = f"{request.base_url}{request.url.path[1:]}{pid}"
        tool = ToolInfo(id=pid,
                        self_=url,
                        type="vm",  # @TODO: Determine type based on tool_info
                        name=tool_info.get("name"),
                        description=tool_info.get("description"),
                        blueprint=tool_info.get("toscaFile"),
                        blueprint_type="tosca",
                        author_name=tool_info.get("author"),)
        tools.append(tool)

    page = PageOfTools(from_=from_, limit=limit, elements=tools, count=tools_info.get("totalElements"))
    return page


# GET /{tool_id}
@router.get("/{tool_id}",
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
             user_info=Depends(authenticate)):
    """Get information about an existing tool blueprint

    :rtype: ToolInfo
    """
    tool_id = tool_id.replace("_", "%2F")
    response = requests.get(TOOLS_MARKET_URL + "/tools/api/v1/by-pid/%s" % tool_id,
                            headers={"Authorization": "Bearer %s" % user_info['token']},
                            timeout=10)
    if response.status_code == 404:
        msg = Error(description="Tool not found")
        return Response(content=msg.model_dump_json(), status_code=404, media_type="application/json")
    elif response.status_code != 200:
        logger.error("Failed to fetch tools from market: %s", response.text)
        msg = Error(description="Failed to fetch tools from market")
        return Response(content=msg.model_dump_json(), status_code=503, media_type="application/json")

    tool_info = response.json()

    if tool_info.get("pid") is None:
        msg = Error(description="Tool not found")
        return Response(content=msg.model_dump_json(), status_code=404, media_type="application/json")

    tool = ToolInfo(id=tool_id,
                    self_=str(request.url),
                    name=tool_info.get("name"),
                    description=tool_info.get("description"),
                    blueprint=tool_info.get("toscaFile"),
                    blueprint_type="tosca",
                    type="vm"  # @TODO: Determine type based on tool_info
                    )

    return tool
