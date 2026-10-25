import base64
import time

import jwt
from flask import Flask, jsonify, request

import db
from key_manager import deserialize_key, ensure_keys

app = Flask(__name__)


def int_to_base64url(value):

    length = (value.bit_length() + 7) // 8
    data = value.to_bytes(length, "big")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


@app.route("/.well-known/jwks.json", methods=["GET"])
def jwks():

    keys = []
    for kid, pem, _exp in db.get_valid_keys():
        numbers = deserialize_key(pem).public_key().public_numbers()
        keys.append({
            "kty": "RSA",
            "kid": str(kid),
            "use": "sig",
            "alg": "RS256",
            "n": int_to_base64url(numbers.n),
            "e": int_to_base64url(numbers.e),
        })
    return jsonify({"keys": keys})


@app.route("/auth", methods=["POST"])
def auth():
    """Mock login: sign and return a JWT.

    ?expired present -> sign with an expired key and an expired exp claim.
    Otherwise         -> sign with a valid key.
    Whatever credentials are sent (Basic auth or JSON) are accepted.
    """
    use_expired = "expired" in request.args
    ensure_keys()  # recreate keys if the DB was deleted while running
    row = db.get_key(expired=use_expired)
    if row is None:
        return jsonify({"error": "no suitable key found"}), 500

    kid, pem, exp = row
    payload = {
        "sub": "userABC",
        "iat": int(time.time()),
        "exp": exp,  # matches the key: in the past when expired
    }
    token = jwt.encode(
        payload,
        deserialize_key(pem),
        algorithm="RS256",
        headers={"kid": str(kid)},
    )
    return token, 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    ensure_keys()
    app.run(host="0.0.0.0", port=8080)
