from fastapi import Response
from awm.models.error import Error


def return_error(message: str, status_code: int = 500) -> Response:
    err = Error(id=f"{status_code}", description=message)
    return Response(content=err.model_dump_json(exclude_unset=True),
                    status_code=status_code,
                    media_type="application/json")
