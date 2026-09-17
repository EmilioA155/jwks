from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta


def generate_key(kid, expires_at):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    return {
        "kid": kid,
        "private_key": private_key,
        "public_key": private_key.public_key(),
        "expires_at": expires_at
    }


active_key = generate_key(
    "active-key",
    datetime.utcnow() + timedelta(days=1)
)

expired_key = generate_key(
    "expired-key",
    datetime.utcnow() - timedelta(days=1)
)
