# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from awm.models.deployment import Deployment  # noqa: E501
from awm.models.deployment_info import DeploymentInfo  # noqa: E501
from awm.models.error import Error  # noqa: E501
from awm.models.page_of_deployments import PageOfDeployments  # noqa: E501
from awm.models.success import Success  # noqa: E501
from awm.test import BaseTestCase


class TestDeploymentsController(BaseTestCase):
    """DeploymentsController integration test stubs"""

    def test_delete_deployment(self):
        """Test case for delete_deployment

        Tear down an existing deployment
        """
        response = self.client.open(
            '/deployment/{deploymentId}',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_deploy_workload(self):
        """Test case for deploy_workload

        Deploy workload to an EOSC environment or an infrastructure for which the user has credentials 
        """
        body = Deployment()
        response = self.client.open(
            '/deployments',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_deployment(self):
        """Test case for get_deployment

        Get information about an existing deployment
        """
        response = self.client.open(
            '/deployment/{deploymentId}',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_deployments(self):
        """Test case for list_deployments

        List existing deployments
        """
        query_string = [('_from', Object()),
                        ('limit', Object()),
                        ('all_nodes', Object())]
        response = self.client.open(
            '/deployments',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
