import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import db

ONE_HOUR = 3600


def generate_private_key():

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def serialize_key(private_key):

    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS1
        encryption_algorithm=serialization.NoEncryption(),
    )


def deserialize_key(pem):

    return serialization.load_pem_private_key(pem, password=None)


def ensure_keys(db_file=None):


    Keys are only generated when missing, so they persist across restarts.
    """
    db.init_db(db_file)
    now = int(time.time())

    if db.get_key(expired=False, db_file=db_file) is None:
        db.save_key(serialize_key(generate_private_key()),
                    now + ONE_HOUR, db_file)

    if db.get_key(expired=True, db_file=db_file) is None:
        db.save_key(serialize_key(generate_private_key()),
                    now - ONE_HOUR, db_file)