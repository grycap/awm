from awm.oidc.client import OpenIDClient
from connexion.exceptions import OAuthProblem


def check_OIDC(token):
    try:
        expired, _ = OpenIDClient.is_access_token_expired(token)
        if expired:
            raise OAuthProblem("Token expired")
        success, user_info = OpenIDClient.get_user_info_request(token)
        if not success:
            return None
    except Exception:
        return None

    user_info["token"] = token
    return user_info
