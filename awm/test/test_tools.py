# coding: utf-8
import pytest
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


@patch("requests.get")
def test_list_tools(requests_get, check_oidc_mock, client, headers):
    tm_response = MagicMock(["status_code", "json"])
    tm_response.status_code = 200
    tm_response.json.return_value = {
        "content": [
            {
                "id": 1,
                "pid": "21.11162/AoQG3Q",
                "name": "Simple Compute Node",
                "author": "EU Node",
                "description": "Desc",
                "toscaFile": "tosca template",
                "publishStatus": "REJECTED",
                "authorUserSub": "user@eosc-federation.eu",
            }
        ],
        "pageNumber": 0,
        "pageSize": 10,
        "totalElements": 1
    }
    requests_get.return_value = tm_response
    response = client.get('/tools/?from=0&limit=10', headers=headers)
    assert response.status_code == 200
    expected_res = {
        "from": 0,
        "limit": 10,
        "count": 1,
        "self": None,
        "prevPage": None,
        "nextPage": None,
        "elements": [
            {
                "kind": "ToolInfo",
                "type": "vm",
                "blueprint": "tosca template",
                "blueprint_type": "tosca",
                "name": "Simple Compute Node",
                "description": "Desc",
                "author_name": "EU Node",
                "author_email": None,
                "organisation": None,
                "keywords": [],
                "license": None,
                "version": None,
                "version_from": None,
                "repository": None,
                "helpdesk": None,
                "validated": False,
                "validated_on": None,
                "self": "http://testserver/tools/21.11162_AoQG3Q"
            }
        ]
    }
    assert response.json() == expected_res


@patch("requests.get")
def test_get_tool(requests_get, check_oidc_mock, client, headers):
    tm_response = MagicMock(["status_code", "json"])
    tm_response.status_code = 200
    tm_response.json.return_value = {
        "id": 1,
        "pid": "21.11162/AoQG3Q",
        "name": "Simple Compute Node",
        "author": "EU Node",
        "description": "Desc",
        "toscaFile": "tosca template",
        "publishStatus": "REJECTED",
        "authorUserSub": "user@eosc-federation.eu"
    }
    requests_get.return_value = tm_response
    response = client.get('/tools/1', headers=headers)
    assert response.status_code == 200
    expected_res = {
        'kind': 'ToolInfo',
        'type': 'vm',
        'blueprint': 'tosca template',
        'blueprint_type': 'tosca',
        'name': 'Simple Compute Node',
        'description': 'Desc',
        'author_name': None,
        'author_email': None,
        'organisation': None,
        'keywords': [],
        'license': None,
        'version': None,
        'version_from': None,
        'repository': None,
        'helpdesk': None,
        'validated': False,
        'validated_on': None,
        'self': 'http://testserver/tools/1'
    }
    assert response.json() == expected_res
