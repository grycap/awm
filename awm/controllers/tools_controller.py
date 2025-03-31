import requests
from connexion import request
from awm.models.page_of_tools import PageOfTools
from awm.models.tool_info import ToolInfo
from connexion.context import context


TOOLS_MARKET_URL = "https://api.eosc.athenarc.gr"


def get_tool(tool_id):
    """Get information about a tool blueprint

    :rtype: ToolInfo
    """
    token = context.get("token_info", {}).get("token")
    response = requests.get(TOOLS_MARKET_URL + "/tools/api/v1/by-pid/%s" % tool_id,
                            headers={"Authorization": "Bearer %s" % token})
    response.raise_for_status()
    tool_info = response.json()
    tool = ToolInfo(_id=tool_id,
                    _self=str(request.url),
                    name=tool_info.get("name"),
                    description=tool_info.get("description1"),
                    blueprint=tool_info.get("toscaFile"),
                    blueprint_type="TOSCA",
                    author_name=tool_info.get("author"),
                    author_email=tool_info.get("email"),
                    _license=tool_info.get("license"),
                    repository=tool_info.get("githubRepo"),
                    helpdesk=tool_info.get("helpdeskPage"))
    # @TODO: Add the rest of the fields
    return tool.to_dict()


def list_tools(all_nodes, from_=None, limit=None):
    """List all tool blueprints

    :param all_nodes: Return tools from all nodes
    :type all_nodes: bool
    :param from_: Index of the first element to return
    :type from_: int
    :param limit: Maximum number of elements to return
    :type limit: int

    :rtype: PageOfTools
    """
    token = context.get("token_info", {}).get("token")
    response = requests.get(TOOLS_MARKET_URL + "/tools/api/v1?pageSize=%s&from=%s" % (limit, from_),
                            headers={"Authorization": "Bearer %s" % token})
    response.raise_for_status()
    tools_info = response.json()

    all = []
    for tool_info in tools_info.get("content"):
        pid = tool_info.get("pid").replace("/", "%2F")
        url = f"{request.base_url}{request.url.path[1:]}/{pid}"
        tool = ToolInfo(_id=pid,
                        _self=url,
                        name=tool_info.get("name"),
                        description=tool_info.get("description1"),
                        blueprint=tool_info.get("toscaFile"),
                        blueprint_type="TOSCA",
                        author_name=tool_info.get("author"),)
        all.append(tool)

    page = PageOfTools(_from=from_, limit=limit, elements=all, count=tools_info.get("totalElements"))
    return page.to_dict()
