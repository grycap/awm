# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from awm.models.error import Error  # noqa: E501
from awm.models.user_info import UserInfo  # noqa: E501
from awm.test import BaseTestCase


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def test_get_user_info(self):
        """Test case for get_user_info

        Retrieve information about the user
        """
        response = self.client.open(
            '/user/info',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
