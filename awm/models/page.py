from awm.models.base_model_ import Model
from typing import List
from awm import util
from connexion import request


class Page(Model):
    """Page Base class for pagination"""
    path = '/'

    def __init__(self, _from: int = None, limit: int = None, elements: List = None, count: int = None):  # noqa: E501
        """Page - a model defined in Swagger

        :param _from: The _from of this Page.  # noqa: E501
        :type _from: int
        :param limit: The limit of this Page.  # noqa: E501
        :type limit: int
        :param count: The count of this Page.  # noqa: E501
        :type count: int
        """
        self.swagger_types = {
            '_from': int,
            'limit': int,
            'count': int,
            '_self': str,
            'prev_page': str,
            'next_page': str,
            'elements': List
        }

        self.attribute_map = {
            '_from': 'from',
            'limit': 'limit',
            'count': 'count',
            '_self': 'self',
            'prev_page': 'prevPage',
            'next_page': 'nextPage',
            'elements': 'elements'
        }
        self.__from = _from
        self._limit = limit
        self._elements = elements
        self._count = count

        self.__self = str(request.url)
        self._prev_page = None
        if self._from > 0:
            self._prev_page = f"{request.base_url}{self.path}"
            _from = self._from - self._limit
            if _from < 0:
                _from = 0
            self._prev_page += f"?from={_from}&limit={self._limit}"
        self._next_page = None
        if self._from + self._limit < self._count:
            self._next_page = f"{request.base_url}{self.path}"
            self._next_page += f"?from={self._from + self._limit}&limit={self._limit}"

    @classmethod
    def from_dict(cls, dikt) -> 'Page':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Page of this Page.  # noqa: E501
        :rtype: Page
        """
        return util.deserialize_model(dikt, cls)

    @property
    def _from(self) -> int:
        """Gets the _from of this Page.

        Index of the first returned element  # noqa: E501

        :return: The _from of this Page.
        :rtype: int
        """
        return self.__from

    @_from.setter
    def _from(self, _from: int):
        """Sets the _from of this Page.

        Index of the first returned element  # noqa: E501

        :param _from: The _from of this Page.
        :type _from: int
        """
        if _from is None:
            raise ValueError("Invalid value for `_from`, must not be `None`")  # noqa: E501

        self.__from = _from

    @property
    def limit(self) -> int:
        """Gets the limit of this Page.

        Maximum number of elements to return at once  # noqa: E501

        :return: The limit of this Page.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit: int):
        """Sets the limit of this Page.

        Maximum number of elements to return at once  # noqa: E501

        :param limit: The limit of this Page.
        :type limit: int
        """
        if limit is None:
            raise ValueError("Invalid value for `limit`, must not be `None`")  # noqa: E501

        self._limit = limit

    @property
    def count(self) -> int:
        """Gets the count of this Page.

        Total number of elements  # noqa: E501

        :return: The count of this Page.
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count: int):
        """Sets the count of this Page.

        Total number of elements  # noqa: E501

        :param count: The count of this Page.
        :type count: int
        """
        if count is None:
            raise ValueError("Invalid value for `count`, must not be `None`")  # noqa: E501

        self._count = count

    @property
    def _self(self) -> str:
        """Gets the _self of this Page.

        Endpoint that returned this page  # noqa: E501

        :return: The _self of this Page.
        :rtype: str
        """
        return self.__self

    @property
    def prev_page(self) -> str:
        """Gets the prev_page of this Page.

        Endpoint that returns the previous page  # noqa: E501

        :return: The prev_page of this Page.
        :rtype: str
        """
        return self._prev_page

    @property
    def next_page(self) -> str:
        """Gets the next_page of this Page.

        Endpoint that returns the next page  # noqa: E501

        :return: The next_page of this Page.
        :rtype: str
        """
        return self._next_page

    @property
    def elements(self) -> List:
        """Gets the elements of this Page.

        List of elements  # noqa: E501

        :return: The elements of this Page.
        :rtype: List
        """
        return self._elements

    @elements.setter
    def elements(self, elements: List):
        """Sets the elements of this Page.

        List of elements  # noqa: E501

        :param elements: The elements of this Page.
        :type elements: List
        """

        self._elements = elements
