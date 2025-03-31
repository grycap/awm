from typing import List
from awm.models.base_model_ import Model
from awm import util


class UserInfo(Model):
    """ UserInfo """
    def __init__(self, base_id: str = None, user_dn: str =None,
                 delegation_id: str = None, dn: List[str] = None, vos: List[str] = None,
                 vos_id: List[str] = None, voms_cred: List[str] = None):  # noqa: E501
        """UserInfo - a model defined in Swagger

        :param kind: The kind of this UserInfo.  # noqa: E501
        :type kind: str
        :param base_id: The base_id of this UserInfo.  # noqa: E501
        :type base_id: str
        :param user_dn: The user_dn of this UserInfo.  # noqa: E501
        :type user_dn: str
        :param delegation_id: The delegation_id of this UserInfo.  # noqa: E501
        :type delegation_id: str
        :param dn: The dn of this UserInfo.  # noqa: E501
        :type dn: List[str]
        :param vos: The vos of this UserInfo.  # noqa: E501
        :type vos: List[str]
        :param vos_id: The vos_id of this UserInfo.  # noqa: E501
        :type vos_id: List[str]
        :param voms_cred: The voms_cred of this UserInfo.  # noqa: E501
        :type voms_cred: List[str]
        """
        self.swagger_types = {
            'kind': str,
            'base_id': str,
            'user_dn': str,
            'delegation_id': str,
            'dn': List[str],
            'vos': List[str],
            'vos_id': List[str],
            'voms_cred': List[str]
        }

        self.attribute_map = {
            'kind': 'kind',
            'base_id': 'base_id',
            'user_dn': 'user_dn',
            'delegation_id': 'delegation_id',
            'dn': 'dn',
            'vos': 'vos',
            'vos_id': 'vos_id',
            'voms_cred': 'voms_cred'
        }
        self._kind = "UserInfo"
        self._base_id = base_id
        self._user_dn = user_dn
        self._delegation_id = delegation_id
        self._dn = dn
        self._vos = vos
        self._vos_id = vos_id
        self._voms_cred = voms_cred

    @classmethod
    def from_dict(cls, dikt) -> 'UserInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UserInfo of this UserInfo.  # noqa: E501
        :rtype: UserInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def kind(self) -> str:
        """Gets the kind of this UserInfo.


        :return: The kind of this UserInfo.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind: str):
        """Sets the kind of this UserInfo.


        :param kind: The kind of this UserInfo.
        :type kind: str
        """

        self._kind = kind

    @property
    def base_id(self) -> str:
        """Gets the base_id of this UserInfo.


        :return: The base_id of this UserInfo.
        :rtype: str
        """
        return self._base_id

    @base_id.setter
    def base_id(self, base_id: str):
        """Sets the base_id of this UserInfo.


        :param base_id: The base_id of this UserInfo.
        :type base_id: str
        """

        self._base_id = base_id

    @property
    def user_dn(self) -> str:
        """Gets the user_dn of this UserInfo.


        :return: The user_dn of this UserInfo.
        :rtype: str
        """
        return self._user_dn

    @user_dn.setter
    def user_dn(self, user_dn: str):
        """Sets the user_dn of this UserInfo.


        :param user_dn: The user_dn of this UserInfo.
        :type user_dn: str
        """

        self._user_dn = user_dn

    @property
    def delegation_id(self) -> str:
        """Gets the delegation_id of this UserInfo.


        :return: The delegation_id of this UserInfo.
        :rtype: str
        """
        return self._delegation_id

    @delegation_id.setter
    def delegation_id(self, delegation_id: str):
        """Sets the delegation_id of this UserInfo.


        :param delegation_id: The delegation_id of this UserInfo.
        :type delegation_id: str
        """

        self._delegation_id = delegation_id

    @property
    def dn(self) -> List[str]:
        """Gets the dn of this UserInfo.


        :return: The dn of this UserInfo.
        :rtype: List[str]
        """
        return self._dn

    @dn.setter
    def dn(self, dn: List[str]):
        """Sets the dn of this UserInfo.


        :param dn: The dn of this UserInfo.
        :type dn: List[str]
        """

        self._dn = dn

    @property
    def vos(self) -> List[str]:
        """Gets the vos of this UserInfo.

        Virtual organisation name(s)  # noqa: E501

        :return: The vos of this UserInfo.
        :rtype: List[str]
        """
        return self._vos

    @vos.setter
    def vos(self, vos: List[str]):
        """Sets the vos of this UserInfo.

        Virtual organisation name(s)  # noqa: E501

        :param vos: The vos of this UserInfo.
        :type vos: List[str]
        """

        self._vos = vos

    @property
    def vos_id(self) -> List[str]:
        """Gets the vos_id of this UserInfo.

        Virtual organisation identifier(s)  # noqa: E501

        :return: The vos_id of this UserInfo.
        :rtype: List[str]
        """
        return self._vos_id

    @vos_id.setter
    def vos_id(self, vos_id: List[str]):
        """Sets the vos_id of this UserInfo.

        Virtual organisation identifier(s)  # noqa: E501

        :param vos_id: The vos_id of this UserInfo.
        :type vos_id: List[str]
        """

        self._vos_id = vos_id

    @property
    def voms_cred(self) -> List[str]:
        """Gets the voms_cred of this UserInfo.


        :return: The voms_cred of this UserInfo.
        :rtype: List[str]
        """
        return self._voms_cred

    @voms_cred.setter
    def voms_cred(self, voms_cred: List[str]):
        """Sets the voms_cred of this UserInfo.


        :param voms_cred: The voms_cred of this UserInfo.
        :type voms_cred: List[str]
        """

        self._voms_cred = voms_cred
