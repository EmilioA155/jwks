from flask import Flask, jsonify, request
from key_manager import active_key, expired_key
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta, timezone
import jwt
import base64

app = Flask(__name__)


def int_to_base64url(value):
    length = (value.bit_length() + 7) // 8
    data = value.to_bytes(length, "big")

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def private_key_to_pem(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


@app.route("/.well-known/jwks.json")
def jwks():

    public_numbers = active_key["public_key"].public_numbers()

    jwk = {
        "kty": "RSA",
        "kid": active_key["kid"],
        "use": "sig",
        "alg": "RS256",
        "n": int_to_base64url(public_numbers.n),
        "e": int_to_base64url(public_numbers.e)
    }

    return jsonify({
        "keys": [jwk]
    })


@app.route("/auth", methods=["POST"])
def auth():

    use_expired = "expired" in request.args

    if use_expired:
        key = expired_key

        payload = {
            "sub": "fake-user",
            "iat": datetime.now(timezone.utc) - timedelta(days=2),
            "exp": datetime.now(timezone.utc) - timedelta(days=1)
        }

    else:
        key = active_key

        payload = {
            "sub": "fake-user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }

    token = jwt.encode(
        payload,
        private_key_to_pem(key["private_key"]),
        algorithm="RS256",
        headers={"kid": key["kid"]}
    )

    return jsonify({
        "token": token
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
