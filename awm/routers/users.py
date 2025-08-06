from fastapi import APIRouter, Depends
from awm.authorization import authenticate
from awm.models.user_info import UserInfo
from awm.models.error import Error


router = APIRouter()


# GET /info
@router.get("/info",
            summary="Retrieve information about the user",
            responses={200: {"model": UserInfo,
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
def get_user_info(user_info=Depends(authenticate)):
    """Retrieve information about the user
    :rtype: UserInfo
    """
    user = UserInfo(base_id=user_info.get("sub"),
                    user_dn=user_info.get("name"),
                    vos=user_info.get("eduperson_entitlement"))
    return user
