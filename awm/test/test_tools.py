# coding: utf-8
import pytest
import base64
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from awm.__main__ import create_app
from pydantic import HttpUrl
from awm.utils.node_registry import EOSCNode


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


@pytest.fixture
def repo_mock(mocker):
    repo = mocker.MagicMock()
    mocker.patch("awm.routers.tools.Repository.create", return_value=repo)
    return repo


@pytest.fixture
def list_nodes_mock(mocker):
    return mocker.patch("awm.utils.node_registry.EOSCNodeRegistry.list_nodes")


@pytest.fixture
def requests_get_mock(mocker):
    return mocker.patch("requests.get")


def test_list_tools(client, check_oidc_mock, repo_mock, headers):
    repo_mock.list.return_value = {"elem": {"path": "path", "sha": "version"}}
    repo_mock.get.return_value = "description: DESC\nmetadata:\n  template_name: NAME"

    response = client.get("/tools", headers=headers)
    assert response.status_code == 200

    expected = {
        "count": 1,
        "elements": [{
            "blueprint": "description: DESC\nmetadata:\n  template_name: NAME",
            "blueprintType": "tosca",
            "description": "DESC",
            "id": "path",
            "name": "NAME",
            "self": "http://testserver/tool/path?version=version",
            "type": "vm",
            "version": "version",
        }],
        "from": 0,
        "limit": 100
    }

    assert response.json() == expected


def test_list_tools_remote(
    client, mocker, check_oidc_mock, repo_mock, list_nodes_mock, requests_get_mock, headers
):
    blueprint = "description: DESC\nmetadata:\n  template_name: NAME"
    repo_mock.list.return_value = {"elem": {"path": "path", "sha": "version"}}
    repo_mock.get.return_value = blueprint

    node1 = EOSCNode(awmAPI=HttpUrl("http://server1.com"), nodeId="n1")
    node2 = EOSCNode(awmAPI=HttpUrl("http://server2.com"), nodeId="n2")
    list_nodes_mock.return_value = [node1, node2]

    # Mock remotos
    resp1 = mocker.MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {
        "count": 1,
        "elements": [{
            "blueprint": blueprint,
            "blueprintType": "tosca",
            "id": "tool1",
            "type": "vm",
        }],
        "from": 0,
        "limit": 100,
    }

    resp2 = mocker.MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "count": 2,
        "elements": [
            {"blueprint": blueprint, "blueprintType": "tosca", "id": "tool2", "type": "vm"},
            {"blueprint": blueprint, "blueprintType": "tosca", "id": "tool3", "type": "vm"},
        ],
        "from": 0,
        "limit": 100,
    }

    requests_get_mock.side_effect = [resp1, resp2, resp1, resp1, resp1, resp2]

    # 1) Sin paginación
    response = client.get("/tools?allNodes=true", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 4
    assert len(response.json()["elements"]) == 4

    requests_get_mock.assert_any_call(
        "http://server1.com/tools?from0&limit=99",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )
    requests_get_mock.assert_any_call(
        "http://server2.com/tools?from0&limit=98",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )

    # 2) from=1 limit=2
    response = client.get("/tools?allNodes=true&from=1&limit=2", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 3
    assert len(response.json()["elements"]) == 2

    requests_get_mock.assert_any_call(
        "http://server1.com/tools?from0&limit=2",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )
    requests_get_mock.assert_any_call(
        "http://server2.com/tools?from0&limit=1",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )

    # 3) from=3 limit=2
    response = client.get("/tools?allNodes=true&from=3&limit=2", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 4
    assert len(response.json()["elements"]) == 1


def test_get_tool(client, check_oidc_mock, repo_mock, headers):
    repo_response = repo_mock.get.return_value = MagicMock()
    repo_response.status_code = 200
    repo_response.json.return_value = {
        "sha": "version",
        "content": base64.b64encode(
            b"description: DESC\nmetadata:\n  template_name: NAME"
        ).decode()
    }

    response = client.get("/tool/toolid", headers=headers)
    assert response.status_code == 200

    expected = {
        "blueprint": "description: DESC\nmetadata:\n  template_name: NAME",
        "blueprintType": "tosca",
        "description": "DESC",
        "id": "toolid",
        "name": "NAME",
        "self": "http://testserver/tool/toolid?version=version",
        "type": "vm",
        "version": "version"
    }

    assert response.json() == expected
    repo_mock.get.assert_called_once_with("toolid", 'latest')

    # Query con version
    response = client.get("/tool/toolid?version=version", headers=headers)
    assert response.status_code == 200
    assert response.json() == expected
    assert repo_mock.get.call_args_list[1][0] == ("toolid", "version")
