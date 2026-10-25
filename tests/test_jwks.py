import time

import db
import key_manager


def test_jwks_endpoint(client):
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    keys = response.get_json()["keys"]
    assert len(keys) == 1  # only the unexpired key
    key = keys[0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["kid"].isdigit()


def test_jwks_lists_all_valid_keys(client):
    pem = key_manager.serialize_key(key_manager.generate_private_key())
    db.save_key(pem, time.time() + 3600)
    keys = client.get("/.well-known/jwks.json").get_json()["keys"]
    assert len(keys) == 2


def test_jwks_post_not_allowed(client):
    assert client.post("/.well-known/jwks.json").status_code == 405
    