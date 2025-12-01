from fastapi import APIRouter, Response
from awm.models.success import Success
from awm import __version__


router = APIRouter()


# GET /version
@router.get("/version",
            summary="Return service version information",
            responses={200: {"model": Success,
                             "description": "Success"}})
def version():
    return Response(content=Success(message=__version__).model_dump_json(),
                    media_type="application/json")
