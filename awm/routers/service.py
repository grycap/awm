from fastapi import APIRouter
from awm.models.success import Success
from awm import __version__


router = APIRouter()


# GET /version
@router.get("/version",
            summary="Return service version information",
            responses={200: {"model": Success,
                             "description": "Success"}})
def version():
    return Success(message=__version__)
