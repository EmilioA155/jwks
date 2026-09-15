from flask import Flask, jsonify
from key_manager import active_key
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

app = Flask(__name__)


def int_to_base64url(value):
    length = (value.bit_length() + 7) // 8
    data = value.to_bytes(length, "big")

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
