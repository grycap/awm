# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from awm.models.error import Error  # noqa: E501
from awm.models.page_of_tools import PageOfTools  # noqa: E501
from awm.models.tool_info import ToolInfo  # noqa: E501
from awm.test import BaseTestCase


class TestToolsController(BaseTestCase):
    """ToolsController integration test stubs"""

    def test_get_tool(self):
        """Test case for get_tool

        Get information about a tool blueprint
        """
        response = self.client.open(
            '/tool/{toolId}',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_tools(self):
        """Test case for list_tools

        List all tool blueprints
        """
        query_string = [('_from', 10),
                        ('limit', 20),
                        ('all_nodes', False)]
        response = self.client.open(
            '/tools',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
