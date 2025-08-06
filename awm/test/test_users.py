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


@patch('awm.authorization.check_OIDC')
def test_user_info(check_oidc_mock, client, headers):
    """Test case for get_user_info

    Retrieve information about the user
    """
    user_info = {
        "sub": "user123",
        "name": "User DN",
        "eduperson_entitlement": ["vos1", "vos2"]
    }
    check_oidc_mock.return_value = user_info
    response = client.get('/user/info', headers=headers)
    assert response.status_code == 200
    user_json = response.json()
    assert user_json["base_id"] == user_info["sub"]
    assert user_json["user_dn"] == user_info["name"]
    assert user_json["vos"] == user_info["eduperson_entitlement"]
