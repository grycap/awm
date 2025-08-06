# coding: utf-8
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from awm.__main__ import create_app


@pytest.fixture
def client():
    return TestClient(app=create_app())


@pytest.fixture
def headers():
    return {"Authorization": "Bearer you-very-secret-token"}


@pytest.fixture
def check_oidc_mock():
    with patch('awm.authorization.check_OIDC') as mock_func:
        mock_func.return_value = {
            "sub": "user123",
            "name": "User DN",
            "eduperson_entitlement": ["vos1", "vos2"],
            "token": "token"
        }
        yield mock_func


def test_list_deployments(check_oidc_mock, client, headers):
    response = client.get('/deployments/', headers=headers)
    assert response.status_code == 200


def test_get_deployment(check_oidc_mock, client, headers):
    response = client.get('/deployments/1', headers=headers)
    assert response.status_code == 404


def test_delete_deployment(check_oidc_mock, client, headers):
    response = client.delete('/deployments/1', headers=headers)
    assert response.status_code == 404


@patch("im_client.IMClient.init_client")
def test_deploy_workload(mock_init_client, check_oidc_mock, client, headers):
    deployment = {
        "tool": {
            "kind": "ToolInfo",
            "blueprint_type": "tosca",
            "blueprint": "tosca template",
            "type": "vm"
        },
        "allocation": {
            "kind": "CredentialsKubernetes",
            "host": "http://k8s.io"
        }
    }
    im_client_mock = MagicMock(["create"])
    im_client_mock.create.return_value = True, "inf_id"
    mock_init_client.return_value = im_client_mock
    response = client.post('/deployments/', headers=headers, data=json.dumps(deployment))
    im_client_mock.create.assert_called_once_with("tosca template", "yaml", True)
    assert response.status_code == 201
    assert response.json() == {"kind": "DeploymentId", "id": "inf_id",
                               'self_': 'http://testserver/deployments//inf_id'}
