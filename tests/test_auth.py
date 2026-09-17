from app import app

def test_auth_returns_token():
    client = app.test_client()

    response = client.post('/auth')

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data


def test_expired_auth_returns_token():
    client = app.test_client()

    response = client.post('/auth?expired=true')

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data


def test_get_auth_not_allowed():
    client = app.test_client()

    response = client.get('/auth')

    assert response.status_code == 405

