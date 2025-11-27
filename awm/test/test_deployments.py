import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from awm.models.tool import ToolId
from awm.__main__ import create_app


@pytest.fixture
def client():
    return TestClient(app=create_app())


@pytest.fixture
def db_mock(mocker):
    """Mock genérico para DataBase, retornando una instancia configurable."""
    instance = MagicMock()
    instance.connect.return_value = True
    mocker.patch("awm.routers.deployments.DataBase", return_value=instance)
    return instance


@pytest.fixture
def check_oidc_mock(mocker):
    """Mock para check_OIDC."""
    mocked = mocker.patch("awm.authorization.check_OIDC")
    mocked.return_value = {"sub": "test-user", "token": "astoken"}
    return mocked


@pytest.fixture
def im_mock(mocker):
    """Mock para IMClient."""
    mocked = mocker.patch("awm.routers.deployments.IMClient.init_client")
    im_mocked = MagicMock()
    mocked.return_value = im_mocked
    return im_mocked


@pytest.fixture
def allocation_mock(mocker):
    """Mock para _get_allocation con un entorno estándar Kubernetes."""
    ainfo = MagicMock()
    ainfo.allocation.root = MagicMock()
    ainfo.allocation.root.kind = "KubernetesEnvironment"
    ainfo.allocation.root.host = "http://some.url/"
    return mocker.patch("awm.routers.allocations._get_allocation", return_value=ainfo)


def _get_deployment_info():
    return ('{"id": "dep_id", '
            '"deployment": {"tool": {"kind": "ToolId", "id": "toolid", '
            '"version": "latest", "infoLink": "http://some.url"}, '
            '"allocation": {"kind": "AllocationId", "id": "aid", "infoLink": "http://some.url"}}, '
            '"status": "pending", "self_": "http://some.url/deployment/dep_id"}')


def test_list_deployments(client, db_mock, check_oidc_mock):
    selects = [
        [[_get_deployment_info()]],
        [[1]]
    ]
    db_mock.select.side_effect = selects

    response = client.get("/deployments",
                          headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["elements"][0]["id"] == "dep_id"

    db_mock.select.assert_any_call(
        "SELECT data FROM deployments WHERE owner = %s order by created LIMIT %s OFFSET %s",
        ("test-user", 100, 0)
    )

    db_mock.select.assert_any_call(
        "SELECT count(id) from deployments WHERE owner = %s",
        ("test-user",)
    )


def test_get_deployment(client, db_mock, check_oidc_mock, im_mock, allocation_mock):
    db_mock.select.side_effect = [
        [[_get_deployment_info()]]
    ]

    im_mock.get_infra_property.return_value = True, {"state": "running"}

    response = client.get("/deployment/dep_id",
                          headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert response.json()["deployment"]["tool"]["id"] == "toolid"

    db_mock.select.assert_called_with(
        "SELECT data FROM deployments WHERE id = %s and owner = %s",
        ("dep_id", "test-user")
    )


def test_delete_deployment(client, db_mock, check_oidc_mock, im_mock, allocation_mock):
    db_mock.select.side_effect = [
        [[_get_deployment_info()]]
    ]

    im_mock.destroy.return_value = True, ""

    response = client.delete("/deployment/dep_id",
                             headers={"Authorization": "Bearer token"})

    assert response.status_code == 202
    assert response.json() == {"message": "Deleting"}

    db_mock.execute.assert_called_with(
        "DELETE FROM deployments WHERE id = %s",
        ("dep_id",)
    )


@pytest.fixture
def get_tool_mock(mocker):
    tool = MagicMock()
    tool.blueprint = "tool blueprint"
    return mocker.patch("awm.routers.tools.get_tool_from_repo", return_value=(tool, 200))


def test_deploy_workload(
    client, db_mock, check_oidc_mock, im_mock, get_tool_mock, allocation_mock
):
    im_mock.create.return_value = True, "new_dep_id"

    payload = ('{"tool": {"kind": "ToolId", "id": "toolid"}, '
               '"allocation": {"kind": "AllocationId", "id": "aid"}}')

    response = client.post("/deployments",
                           headers={"Authorization": "Bearer token"},
                           data=payload)

    assert response.status_code == 202
    assert response.json()["id"] == "new_dep_id"
    assert response.json()["infoLink"] == "http://testserver/deployment/new_dep_id"
