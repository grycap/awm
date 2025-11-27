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


@pytest.fixture
def db_mock(mocker):
    """Mock genérico para DataBase, retornando una instancia configurable."""
    instance = MagicMock()
    instance.connect.return_value = True
    mocker.patch("awm.routers.allocations.DataBase", return_value=instance)
    return instance


def _get_allocation_info():
    return '{"kind": "KubernetesEnvironment", "host": "http://some.url/"}'


def test_list_allocations(check_oidc_mock, client, headers):
    response = client.get('/allocations/', headers=headers)
    assert response.status_code == 200


def test_get_allocation(check_oidc_mock, db_mock, client, headers):
    selects = [
        [["1", _get_allocation_info()]],
        [[1]]
    ]
    db_mock.select.side_effect = selects

    response = client.get('/allocation/1', headers=headers)
    assert response.status_code == 200
