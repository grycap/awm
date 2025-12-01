import logging
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from awm.oidc.client import OpenIDClient

# Middleware de seguridad HTTP para Bearer Token
security = HTTPBearer(
    scheme_name="OIDC",
    description="OpenID Connect access token for authentication",
    bearerFormat="JWT"
)
logger = logging.getLogger(__name__)


def authenticate(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    user_info = check_OIDC(token)
    if user_info is None:
        raise HTTPException(status_code=401, detail="Authorization required")
    return user_info


def check_OIDC(token):
    try:
        expired, _ = OpenIDClient.is_access_token_expired(token)
        if expired:
            raise HTTPException(status_code=401, detail="Token expired")
        success, user_info = OpenIDClient.get_user_info_request(token)
        if not success:
            return None
    except Exception:
        logger.exception("Error checking OIDC token")
        return None

    user_info["token"] = token
    return user_info
