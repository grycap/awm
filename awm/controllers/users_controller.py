from awm.models.user_info import UserInfo
from connexion.context import context


def get_user_info():
    """Retrieve information about the user
    :rtype: UserInfo
    """
    user_info = context.get("token_info", {})
    user = UserInfo(base_id=user_info.get("sub"),
                    user_dn=user_info.get("name"),
                    vos=user_info.get("eduperson_entitlement"))
    return user.to_dict()
