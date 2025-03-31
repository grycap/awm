import os
from connexion import request
from awm.models.deployment_info import DeploymentInfo
from awm.models.page_of_deployments import PageOfDeployments
from awm.models.success import Success
from awm.controllers.tools_controller import get_tool
from awm.im.im import InfrastructureManager
from connexion.context import context

IM_URL = "http://localhost:8080"


def delete_deployment(deployment_id):
    """Tear down an existing deployment

    :rtype: Success
    """
    # @TODO: get the deployment from the Database
    # @TODO: create the IM auth header
    # @TODO: delete the deployment from the IM
    # @TODO: delete the deployment from the Database
    msg = Success(message=f"Deployment {deployment_id} deleted successfully")
    return msg.to_dict(), 204


def deploy_workload(body):
    """Deploy workload to an EOSC environment or an infrastructure for which the user has credentials 

    :param body: 
    :type body: dict | bytes

    :rtype: DeploymentId
    """

    tool_id = body.get("tool").get("id")
    blueprint = get_tool(tool_id).get("blueprint")

    token = context.get("token_info", {}).get("token")
    allocation = body.get("allocation")
    auth_data = "type = InfrastructureManager; token = %s" % token
    if allocation.get("kind") == "EoscNodeAllocation":
        # @TODO: Implement deployment to EOSC
        pass
    elif allocation.get("kind") == "CredentialsOpenStack":
        auth_data += "\\n type = OpenStack; auth_version = 3.x_oidc_access_token"
        auth_data += "; username = %s" % allocation.get("userName")
        auth_data += "; password = %s" % token
        auth_data += "; tenant = %s" % allocation.get("tenant")
        auth_data += "; host = %s" % allocation.get("host")
        auth_data += "; domain = %s" % allocation.get("domain")
        auth_data += "; region = %s" % allocation.get("region")
        # @TODO: Add all the other parameters
    elif allocation.get("kind") == "CredentialsKubernetes":
        # @TODO: Implement deployment to EOSC
        auth_data += "\\n type = Kubernetes; token = %s" % token
    else:
        raise ValueError("Allocation kind not supported")

    # Create the infrastructure in the IM
    # im = InfrastructureManager(IM_URL)
    # response = im.create_inf(blueprint, auth_data)
    # response.raise_for_status()
    # inf_id = os.path.basename(response.text)

    # @TODO: Store the deployment information in the database
    deployment_id = "1"
    return {"id": deployment_id,
            "kind": "DeploymentId",
            "self": f"{request.url}/{deployment_id}"}


def get_deployment(deployment_id):
    """Get information about an existing deployment

    :rtype: DeploymentInfo
    """
    deployment = DeploymentInfo(_id=deployment_id, status="configured", _self=str(request.url))
    return deployment.to_dict()


def list_deployments(all_nodes, from_=None, limit=None):
    """List existing deployments

    :param all_nodes: List deployments in all nodes
    :type all_nodes: bool
    :param _from: Index of the first element to return
    :type _from: int
    :param limit: Maximum number of elements to return
    :type limit: int

    :rtype: PageOfDeployments
    """
    all = []
    for i in range(0, 15):
        url = f"{request.base_url}{request.url.path[1:]}/{i}"
        all.append(DeploymentInfo(_id=str(i), _self=url))

    page = PageOfDeployments(_from=from_, limit=limit, elements=all[from_:from_ + limit], count=len(all))
    return page.to_dict()
