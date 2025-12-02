#
# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid
import time
import awm
import json
from fastapi import APIRouter, Query, Depends, Request, Response
from awm.authorization import authenticate
from awm.models.allocation import AllocationInfo, Allocation, AllocationId
from awm.models.page import PageOfAllocations
from awm.models.error import Error
from awm.models.success import Success
from awm.utils.db import DataBase
from awm.utils.node_registry import EOSCNodeRegistry
from . import return_error


router = APIRouter()
DB_URL = os.getenv("DB_URL", "file:///tmp/awm.db")


def _init_table(db: DataBase) -> bool:
    """Creates de database."""
    if not db.table_exists("allocations"):
        awm.logger.info("Creating allocations table")
        if db.db_type == DataBase.MYSQL:
            db.execute("CREATE TABLE allocations (id VARCHAR(255) PRIMARY KEY, data TEXT, "
                       "owner VARCHAR(255), created TIMESTAMP)")
        elif db.db_type == DataBase.SQLITE:
            db.execute("CREATE TABLE allocations (id TEXT PRIMARY KEY, data TEXT, "
                       "owner VARCHAR(255), created TIMESTAMP)")
        elif db.db_type == DataBase.MONGO:
            db.connection.create_collection("allocations")
            db.connection["allocations"].create_index([("id", 1), ("owner", 1)], unique=True)
        return True
    return False


# GET /allocations
@router.get("/allocations",
            summary="List all credentials or EOSC environments of the user",
            responses={200: {"model": PageOfAllocations,
                             "description": "Success"},
                       400: {"model": Error,
                             "description": "Invalid parameters or configuration"},
                       401: {"model": Error,
                             "description": "Authorization required"},
                       403: {"model": Error,
                             "description": "Forbidden"},
                       419: {"model": Error,
                             "description": "Re-delegate credentials"},
                       503: {"model": Error,
                             "description": "Try again later"}})
def list_allocations(
    request: Request,
    from_: int = Query(0, alias="from", ge=0,
                       description="Index of the first element to return"),
    limit: int = Query(100, alias="limit", ge=1,
                       description="Maximum number of elements to return"),
    all_nodes: bool = Query(False, alias="allNodes"),
    user_info=Depends(authenticate)
):
    allocations = []
    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        if db.db_type == DataBase.MONGO:
            res = db.find("allocations", filt={"owner": user_info['sub']},
                          projection={"data": True}, sort=[('created', -1)])
            for count, elem in enumerate(res):
                if from_ > count:
                    continue
                allocation_data = elem['data']
                allocation = Allocation.model_validate_json(allocation_data)
                allocation_info = AllocationInfo(
                    id=elem['id'],
                    self_=f"{request.url_root.rstrip('/')}/allocation/{elem['id']}",
                    allocation=allocation
                )
                allocations.append(allocation_info)
                if len(allocations) >= limit:
                    break
            count = len(res)
        else:
            sql = "SELECT id, data FROM allocations WHERE owner = %s order by created LIMIT %s OFFSET %s"
            res = db.select(sql, (user_info['sub'], limit, from_))
            for elem in res:
                allocation_id = elem[0]
                allocation_data = elem[1]
                allocation = Allocation.model_validate_json(allocation_data)
                allocation_info = AllocationInfo(
                    id=allocation_id,
                    self_=str(request.url_for("get_allocation", allocation_id=allocation_id)),
                    allocation=allocation
                )
                allocations.append(allocation_info)
            res = db.select("SELECT count(id) from allocations WHERE owner = %s", (user_info['sub'],))
            count = res[0][0] if res else 0
        db.close()
    else:
        return return_error("Database connection failed", 503)

    if all_nodes:
        remote_count, remote_tools = EOSCNodeRegistry.list_allocations(from_, limit, count, user_info)
        allocations.extend(remote_tools)
        count += remote_count

    page = PageOfAllocations(from_=from_, limit=limit, elements=allocations, count=count)
    page.set_next_and_prev_pages(request, all_nodes)
    return Response(content=page.model_dump_json(exclude_unset=True, by_alias=True),
                    status_code=200, media_type="application/json")


def _get_allocation(allocation_id: str, user_info: dict, request: Request) -> AllocationInfo:
    allocation_info = None
    user_id = user_info['sub']
    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        if db.db_type == DataBase.MONGO:
            res = db.find("allocations", {"id": allocation_id, "owner": user_id}, {"id": True, "data": True})
        else:
            res = db.select("SELECT id, data FROM allocations WHERE id = %s and owner = %s", (allocation_id, user_id))
        db.close()
        if res:
            if db.db_type == DataBase.MONGO:
                allocation_id = res[0]["id"]
                allocation_data = res[0]["data"]
            else:
                allocation_id = res[0][0]
                allocation_data = res[0][1]
            allocation = Allocation.model_validate_json(allocation_data)
            allocation_info = AllocationInfo(
                id=allocation_id,
                self_=str(request.url_for("get_allocation", allocation_id=allocation_id)),
                allocation=allocation
            )
    else:
        awm.logger.error("Database connection failed")
        return None

    return allocation_info


# GET /allocation/{allocation_id}
@router.get("/allocation/{allocation_id}",
            summary="Get information about an existing deployment",
            responses={200: {"model": AllocationInfo,
                             "description": "Accepted"},
                       400: {"model": Error,
                             "description": "Invalid parameters or configuration"},
                       401: {"model": Error,
                             "description": "Authorization required"},
                       403: {"model": Error,
                             "description": "Forbidden"},
                       404: {"model": Error,
                             "description": "Not found"},
                       419: {"model": Error,
                             "description": "Re-delegate credentials"},
                       503: {"model": Error,
                             "description": "Try again later"}})
def get_allocation(request: Request,
                   allocation_id,
                   user_info=Depends(authenticate)):
    """Get information about an existing allocation

    :rtype: AllocationInfo
    """
    allocation_info = _get_allocation(allocation_id, user_info, request)
    if allocation_info is None:
        return return_error("Allocation not found", status_code=404)

    return Response(content=allocation_info.model_dump_json(exclude_unset=True, by_alias=True),
                    status_code=200, media_type="application/json")


def _check_allocation_in_use(allocation_id: str, user_info: dict, request: Request) -> Response:
    # check if this allocation is used in any deployment
    response = awm.routers.deployments._list_deployments(user_info=user_info, request=request)
    if response.status_code != 200:
        return response

    for dep_info in json.loads(response.body).get("elements"):
        if dep_info.get('deployment', {}).get('allocation', {}).get('id') == allocation_id:
            return return_error("Allocation in use", 409)

    return None


# PUT /allocation/{allocation_id}
@router.put("/allocation/{allocation_id}",
            summary="Update existing environment of the user",
            responses={200: {"model": AllocationInfo,
                             "description": "Updated"},
                       400: {"model": Error,
                             "description": "Invalid parameters or configuration"},
                       401: {"model": Error,
                             "description": "Authorization required"},
                       403: {"model": Error,
                             "description": "Forbidden"},
                       419: {"model": Error,
                             "description": "Re-delegate credentials"},
                       503: {"model": Error,
                             "description": "Try again later"}})
def update_allocation(allocation_id,
                      request: Request,
                      user_info=Depends(authenticate)):
    allocation_info = _get_allocation(allocation_id, user_info, request)
    if allocation_info is None:
        return return_error("Allocation not found", status_code=404)

    # check if this allocation is used in any deployment
    response = _check_allocation_in_use(allocation_id, user_info, request)
    if response:
        return response

    allocation_id = _create_allocation(allocation_info.allocation,
                                       allocation_id=allocation_id,
                                       user_info=user_info)
    if not allocation_id:
        return return_error("Database connection failed", 503)

    allocation_info = _get_allocation(allocation_id, user_info, request)
    return Response(content=allocation_info.model_dump_json(exclude_unset=True, by_alias=True),
                    status_code=200, media_type="application/json")


# DELETE /allocation/{allocation_id}
@router.delete("/allocation/{allocation_id}",
               summary="Remove existing environment of the user",
               responses={204: {"description": "Accepted"},
                          400: {"model": Error,
                                "description": "Invalid parameters or configuration"},
                          401: {"model": Error,
                                "description": "Authorization required"},
                          403: {"model": Error,
                                "description": "Forbidden"},
                          404: {"model": Error,
                                "description": "Not found"},
                          419: {"model": Error,
                                "description": "Re-delegate credentials"},
                          503: {"model": Error,
                                "description": "Try again later"}})
def delete_allocation(allocation_id,
                      request: Request,
                      user_info=Depends(authenticate)):
    """Remove existing environment of the user

    :rtype: Success
    """
    allocation_info = _get_allocation(allocation_id, user_info, request)
    if allocation_info is None:
        return return_error("Allocation not found", status_code=404)

    # check if this allocation is used in any deployment
    response = _check_allocation_in_use(allocation_id, user_info, request)
    if response:
        return response

    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        if db.db_type == DataBase.MONGO:
            db.delete("allocations", {"id": allocation_id})
        else:
            db.execute("DELETE FROM allocations WHERE id = %s", (allocation_id,))
        db.close()
    else:
        return return_error("Database connection failed", 503)

    msg = Success(message="Deleted")
    return Response(content=msg.model_dump_json(exclude_unset=True),
                    status_code=200,
                    media_type="application/json")


def _create_allocation(allocation: Allocation,
                       allocation_id: str = None,
                       user_info: dict = None):
    db = DataBase(DB_URL)
    if db.connect():
        _init_table(db)
        data = allocation.model_dump_json(exclude_unset=True, by_alias=True)
        if db.db_type == DataBase.MONGO:
            if allocation_id is None:  # new allocation
                allocation_id = str(uuid.uuid4())
                replace = {"id": allocation_id, "data": data,
                           "owner": user_info['sub'],
                           "created": time.time()}
            else:  # update existing allocation
                replace = {"id": allocation_id, "data": data,
                           "owner": user_info['sub']}
            db.replace("allocations", {"id": allocation_id}, replace)
        else:
            if allocation_id is None:  # new allocation
                allocation_id = str(uuid.uuid4())
                sql = "replace into allocations (id, data, owner, created) values (%s, %s, %s, %s)"
                values = (allocation_id, data, user_info['sub'], time.time())
            else:  # update existing allocation
                sql = "update allocations set data = %s where id = %s"
                values = (data, allocation_id)
            db.execute(sql, values)
        db.close()
        return allocation_id
    else:
        return None


# POST /allocations
@router.post("/allocations",
             summary="Record an environment of the user",
             responses={201: {"model": AllocationId,
                              "description": "Accepted"},
                        400: {"model": Error,
                              "description": "Invalid parameters or configuration"},
                        401: {"model": Error,
                              "description": "Authorization required"},
                        403: {"model": Error,
                              "description": "Forbidden"},
                        419: {"model": Error,
                              "description": "Re-delegate credentials"},
                        503: {"model": Error,
                              "description": "Try again later"}})
def create_allocation(allocation: Allocation,
                      request: Request,
                      user_info=Depends(authenticate)):
    """Record an environment of the user
    :rtype: AllocationId
    """
    allocation_id = _create_allocation(allocation, allocation_id=None, user_info=user_info)
    if not allocation_id:
        return return_error("Database connection failed", 503)

    url = str(request.url_for("get_allocation", allocation_id=allocation_id))
    allocation_id_model = AllocationId(id=allocation_id, infoLink=url)
    return Response(content=allocation_id_model.model_dump_json(exclude_unset=True, by_alias=True),
                    status_code=201, media_type="application/json")
