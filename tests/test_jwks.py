from app import app

def test_jwks_endpoint():
    client = app.test_client()

    response = client.get('/.well-known/jwks.json')

    assert response.status_code == 200

    data = response.get_json()

    assert "keys" in data
    assert len(data["keys"]) > 0
