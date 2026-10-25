import jwt

import db


def jwks_lookup(client):

    data = client.get("/.well-known/jwks.json").get_json()
    return {k["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(k)
            for k in data["keys"]}


def test_auth_returns_valid_jwt(client):
    response = client.post("/auth")
    assert response.status_code == 200
    token = response.get_data(as_text=True)

    kid = jwt.get_unverified_header(token)["kid"]
    public_keys = jwks_lookup(client)
    assert kid in public_keys

    claims = jwt.decode(token, public_keys[kid], algorithms=["RS256"])
    assert claims["sub"] == "userABC"


def test_auth_accepts_basic_and_json(client):
    r1 = client.post("/auth", headers={"Authorization": "Basic dTpw"})
    r2 = client.post("/auth", json={"username": "userABC",
                                    "password": "password123"})
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_expired_auth_returns_expired_jwt(client):
    response = client.post("/auth?expired=true")
    assert response.status_code == 200
    token = response.get_data(as_text=True)

    kid = jwt.get_unverified_header(token)["kid"]

    assert kid not in jwks_lookup(client)

    claims = jwt.decode(token, options={"verify_signature": False})
    assert claims["exp"] < claims["iat"]


def test_auth_regenerates_missing_keys(db_file):

    from app import app
    db.init_db()
    response = app.test_client().post("/auth")
    assert response.status_code == 200


def test_auth_500_when_no_key(client, monkeypatch):
    monkeypatch.setattr(db, "get_key", lambda expired=False: None)
    response = client.post("/auth")
    assert response.status_code == 500


def test_get_auth_not_allowed(client):
    assert client.get("/auth").status_code == 405
    assert client.put("/auth").status_code == 405
