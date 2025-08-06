# coding: utf-8
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
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


def test_list_allocations(check_oidc_mock, client, headers):
    response = client.get('/allocations/', headers=headers)
    assert response.status_code == 200


def test_get_allocation(check_oidc_mock, client, headers):
    response = client.get('/allocations/1', headers=headers)
    assert response.status_code == 503
