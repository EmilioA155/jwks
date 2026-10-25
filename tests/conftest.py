import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                "..")))

import db  # noqa: E402
import key_manager  # noqa: E402
from app import app as flask_app  # noqa: E402


@pytest.fixture
def db_file(tmp_path, monkeypatch):

    path = str(tmp_path / "test_keys.db")
    monkeypatch.setattr(db, "DB_FILE", path)
    return path


@pytest.fixture
def client(db_file):

    key_manager.ensure_keys()
    
    return flask_app.test_client()
    