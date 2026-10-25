import sqlite3
import time

import db
import key_manager


def test_schema_created(db_file):
    db.init_db()
    with sqlite3.connect(db_file) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(keys)")]
    assert cols == ["kid", "key", "exp"]


def test_ensure_keys_seeds_one_valid_one_expired(db_file):
    key_manager.ensure_keys()
    assert db.get_key(expired=False) is not None
    assert db.get_key(expired=True) is not None


def test_ensure_keys_does_not_duplicate(db_file):
    key_manager.ensure_keys()
    key_manager.ensure_keys()  # simulate a restart
    with sqlite3.connect(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM keys").fetchone()[0]
    assert count == 2


def test_serialize_roundtrip_is_pkcs1():
    key = key_manager.generate_private_key()
    pem = key_manager.serialize_key(key)
    assert pem.startswith(b"-----BEGIN RSA PRIVATE KEY-----")
    loaded = key_manager.deserialize_key(pem)
    assert loaded.private_numbers() == key.private_numbers()


def test_injection_string_is_stored_as_data(db_file):

    db.init_db()
    evil = b"x'); DROP TABLE keys; --"
    db.save_key(evil, time.time() + 60)
    row = db.get_key(expired=False)
    assert row[1] == evil
    assert len(db.get_valid_keys()) == 1