import os
import logging
from imclient import IMClient
from fastapi import APIRouter, Query, Depends, Request, Response
from awm.authorization import authenticate
from awm.models.allocation import AllocationInfo
from awm.models.page import PageOfAllocations
from awm.models.error import Error
from awm.models.success import Success
from awm.db import DataBase


router = APIRouter()
DB_URL = os.getenv("DB_URL", "file:///tmp/awm.db")
logger = logging.getLogger(__name__)


# GET /
@router.get("/",
            summary="List all credentials or EOSC environments of the user",
            responses={200: {"model": PageOfAllocations,
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
def list_allocations(
    request: Request,
    from_: int = Query(0, alias="from", ge=0,
                       description="Index of the first element to return"),
    limit: int = Query(100, alias="limit", ge=1,
                       description="Maximum number of elements to return"),
    all_nodes: bool = Query(False, alias="allNodes"),
    user_info=Depends(authenticate)
):
    # @TODO: get the allocations from ?
    page = PageOfAllocations(from_=from_, limit=limit, elements=[], count=0)
    return page


# GET /{allocation_id}
@router.get("/{allocation_id}",
            summary="Get information about an existing deployment",
            responses={200: {"model": AllocationInfo,
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
def get_allocation(allocation_id,
                   user_info=Depends(authenticate)):
    """Get information about an existing allocation

    :rtype: AllocationInfo
    """
    return Response(content=Error(description="Not implemented").model_dump_json(), status_code=503, media_type="application/json")
