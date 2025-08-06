# coding: utf-8
import pytest
from fastapi.testclient import TestClient
from awm.__main__ import create_app
from awm import __version__


@pytest.fixture
def client():
    return TestClient(app=create_app())


@pytest.fixture
def headers():
    return {"Authorization": "Bearer you-very-secret-token"}


def test_version(client, headers):
    """Test case for service version

    Retrieve the service version
    """
    response = client.get('/version', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'message': __version__}
