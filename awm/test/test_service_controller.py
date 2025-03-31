# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from awm.models.version import Version  # noqa: E501
from awm.test import BaseTestCase


class TestServiceController(BaseTestCase):
    """ServiceController integration test stubs"""

    def test_version(self):
        """Test case for version

        Return service version information
        """
        response = self.client.open(
            '/version',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
