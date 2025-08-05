import os
import logging
from imclient import IMClient
from fastapi import APIRouter, Query, Depends, Request, Response
from awm.authorization import authenticate
from awm.models.deployment import DeploymentInfo, DeploymentId, Deployment
from awm.models.page import PageOfDeployments
from awm.models.error import Error
from awm.models.success import Success
from awm.db import DataBase


router = APIRouter()
IM_URL = os.getenv("IM_URL", "http://localhost:8080")
DB_URL = os.getenv("DB_URL", "file:///tmp/awm.db")
logger = logging.getLogger(__name__)


def _init_table(db):
    """ Creates de database """
    if not db.table_exists("deployments"):
        logger.info("Creating deployments table")
        if db.db_type == DataBase.MYSQL:
            db.execute("CREATE TABLE deployments (id VARCHAR(255) PRIMARY KEY, data TEXT)")
        elif db.db_type == DataBase.SQLITE:
            db.execute("CREATE TABLE deployments (id TEXT PRIMARY KEY, data TEXT)")
        elif db.db_type == DataBase.MONGO:
            db.connection.create_collection("deployments")
            db.connection["deployments"].create_index([("id", 1)], unique=True)
        db.close()
        return True
    return False


def _get_im_auth_header(token, allocation=None):
    auth_data = f"type = InfrastructureManager; token = {token}"
    if allocation:
        if allocation.get("kind") == "EoscNodeAllocation":
            # @TODO: Implement deployment to EOSC
            pass
        elif allocation.get("kind") == "CredentialsOpenStack":
            auth_data += "\\n type = OpenStack; auth_version = 3.x_oidc_access_token"
            auth_data += f"; username = {allocation.get('userName')}"
            auth_data += f"; password = {token}"
            auth_data += f"; tenant = {allocation.get('tenant')}"
            auth_data += f"; host = {allocation.get('host')}"
            auth_data += f"; domain = {allocation.get('domain')}"
            auth_data += f"; region = {allocation.get('region')}"
            # @TODO: Add all the other parameters
        elif allocation.get("kind") == "CredentialsKubernetes":
            # @TODO: How the TM will get now the token?
            auth_data += f"\\n type = Kubernetes; token = {token}"
        else:
            raise ValueError("Allocation kind not supported")
    return auth_data


def _get_deployment(deployment_id, user_token):
    deployment = None
    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        res = db.select("SELECT id, data FROM deployments WHERE id = %s", (deployment_id,))
        db.close()
        if res:
            deployment_data = res[0][1]
            deployment = DeploymentInfo.model_validate_json(deployment_data)

            auth_data = _get_im_auth_header(user_token, deployment.allocation)
            client = IMClient.init_client(IM_URL, auth_data)
            success, state_info = client.get_infra_property(deployment_id, "state")
            if not success:
                msg = Error(description=state_info)
                return msg, 400
            deployment.status = state_info['state']
        else:
            msg = Error(id="404", description=f"Deployment {deployment_id} not found")
            return msg, 404
    else:
        msg = Error(description="Database connection failed")
        return msg, 503
    return deployment, 200


# GET /
@router.get("/",
            summary="List existing deployments",
            responses={200: {"model": PageOfDeployments,
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
def list_deployments(
    request: Request,
    from_: int = Query(0, alias="from", ge=0,
                       description="Index of the first element to return"),
    limit: int = Query(100, alias="limit", ge=1,
                       description="Maximum number of elements to return"),
    all_nodes: bool = Query(False, alias="allNodes"),
    user_info=Depends(authenticate)
):
    deployments = []
    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        args = []
        sql = "SELECT * FROM deployments"
        if limit is not None:
            sql += " LIMIT %s"
            args = [limit]
        if from_ is not None:
            sql += " OFFSET %s"
            args.append(from_)
        res = db.select(sql, tuple(args))
        for elem in res:
            deployment_data = elem[1]
            deployment_info = DeploymentInfo.model_validate_json(deployment_data)
            # @TODO: Should we get the state from the IM?
            deployments.append(deployment_info)
        res = db.select("SELECT count(id) from deployments")
        count = res[0][0] if res else 0
        db.close()
    else:
        msg = Error(description="Database connection failed")
        return msg.model_dump_json(), 503

    base_url = str(request.base_url)[:-1] + request.url.path
    next_url = f"{base_url}?from={from_ + limit}&limit={limit}" if from_ + limit < len(deployments) else None
    previous_url = f"{base_url}?from={max(0, from_ - limit)}&limit={limit}" if from_ > 0 and len(deployments) > 0 else None
    page = PageOfDeployments(from_=from_, limit=limit, elements=deployments, count=count,
                             self_=str(request.url), nextPage=next_url, prevPage=previous_url)
    return page


# GET /{deployment_id}
@router.get("/{deployment_id}",
            summary="Get information about an existing deployment",
            responses={200: {"model": DeploymentInfo,
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
def get_deployment(deployment_id,
                   user_info=Depends(authenticate)):
    """Get information about an existing deployment

    :rtype: DeploymentInfo
    """
    deployment, status_code = _get_deployment(deployment_id, user_info['token'])
    return Response(content=deployment.model_dump_json(), status_code=status_code, media_type="application/json")


# GET /{deployment_id}
@router.delete("/{deployment_id}",
               summary="Tear down an existing deployment",
               responses={204: {"description": "Accepted"},
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
def delete_deployment(deployment_id,
                      user_info=Depends(authenticate)):
    """Tear down an existing deployment

    :rtype: Success
    """
    deployment, status_code = _get_deployment(deployment_id, user_info['token'])
    if status_code != 200:
        return Response(content=deployment.model_dump_json(), status_code=status_code, media_type="application/json")

    auth_data = _get_im_auth_header(user_info['token'], deployment.allocation)
    client = IMClient.init_client(IM_URL, auth_data)
    success, msg = client.destroy(deployment_id)

    if not success:
        error_msg = Error(description=msg)
        return Response(content=error_msg.model_dump_json(), status_code=400, media_type="application/json")    

    db = DataBase(DB_URL)
    if db.connect():
        db.select("DELETE FROM deployments WHERE id = %s", (deployment_id,))
        db.close()

    return Response(status_code=204)


# POST /
@router.post("/",
             summary="Deploy workload to an EOSC environment or an infrastructure for which the user has credentials",
             responses={201: {"model": DeploymentId,
                              "description": "Accepted"},
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
def deploy_workload(deployment: Deployment,
                    request: Request,
                    user_info=Depends(authenticate)):
    """Deploy workload to an EOSC environment or an infrastructure for which the user has credentials

    :param body: The deployment request body containing the tool and allocation information
    :type body: dict | bytes

    :rtype: DeploymentId
    """

    auth_data = _get_im_auth_header(user_info['token'], deployment.allocation)

    # Create the infrastructure in the IM
    client = IMClient.init_client(IM_URL, auth_data)
    success, deployment_id = client.create(deployment.tool.blueprint, "yaml", True)
    if not success:
        msg = Error(description=deployment_id)
        return msg.to_dict(), 400

    db = DataBase(DB_URL)
    if db.connect():
        deployment = DeploymentInfo(id=deployment_id,
                                    allocation=deployment.allocation,
                                    tool=deployment.tool,
                                    status="pending",
                                    self_=f"{request.url}/{deployment_id}")
        data = deployment.model_dump_json()
        res = db.execute("replace into deployments (id, data) values (%s, %s)", (deployment_id, data))
        db.close()
        if not res:
            msg = Error(description="Failed to store deployment information in the database")
            return Response(content=msg.model_dump_json(), status_code=503, media_type="application/json")
    else:
        msg = Error(description="Database connection failed")
        return Response(content=msg.model_dump_json(), status_code=503, media_type="application/json")

    dep_id = DeploymentId(id=deployment_id, kind="DeploymentId", self_=deployment.self_)
    return Response(content=dep_id.model_dump_json(), status_code=204, media_type="application/json")
