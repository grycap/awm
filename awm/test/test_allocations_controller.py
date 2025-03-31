# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from awm.models.allocation_info import AllocationInfo  # noqa: E501
from awm.models.error import Error  # noqa: E501
from awm.models.page_of_allocations import PageOfAllocations  # noqa: E501
from awm.models.success import Success  # noqa: E501
from awm.test import BaseTestCase


class TestAllocationsController(BaseTestCase):
    """AllocationsController integration test stubs"""

    def test_delete_allocation(self):
        """Test case for delete_allocation

        Delete existing credentials or EOSC environment of the user
        """
        response = self.client.open(
            '/allocation/{allocationId}',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_allocation_info(self):
        """Test case for get_allocation_info

        Retrieve information about existing credentials or EOSC environment of the user
        """
        response = self.client.open(
            '/allocation/{allocationId}',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_allocations(self):
        """Test case for list_allocations

        List all credentials or EOSC environments of the user
        """
        query_string = [('_from', Object()),
                        ('limit', Object()),
                        ('all_nodes', Object())]
        response = self.client.open(
            '/allocations',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_record_allocation(self):
        """Test case for record_allocation

        Record credentials or EOSC environment of the user
        """
        body = Object()
        response = self.client.open(
            '/allocations',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_allocation(self):
        """Test case for update_allocation

        Update existing credentials or EOSC environment of the user
        """
        body = Object()
        response = self.client.open(
            '/allocation/{allocationId}',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
