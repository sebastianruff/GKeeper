import json
from unittest.mock import patch

import pytest
from gkeepapi import exception

from app.keep_client import KeepClientError, build_keep_client, has_credentials, save_credentials


class FakeKeep:
    def __init__(self) -> None:
        self.authenticate_calls = []

    def authenticate(self, email, token, state=None):
        self.authenticate_calls.append((email, token, state))

    def dump(self):
        return {"token": "cached", "nodes": []}


class FakeKeepLoginError(FakeKeep):
    def authenticate(self, email, token, state=None):
        raise exception.LoginException("bad auth")


class FakeKeepUnexpectedError(FakeKeep):
    def authenticate(self, email, token, state=None):
        raise RuntimeError("boom")


@patch("app.keep_client.Keep", return_value=FakeKeep())
def test_build_keep_client_authenticates_and_saves_state(_mock_keep, monkeypatch, tmp_path):
    credentials_path = tmp_path / "credentials.json"
    state_path = tmp_path / "state.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))
    monkeypatch.setenv("GOOGLE_STATE_PATH", str(state_path))

    save_credentials("user@example.com", "master-token")
    keep = build_keep_client()

    assert keep.authenticate_calls == [("user@example.com", "master-token", None)]
    assert state_path.exists()


@patch("app.keep_client.Keep", return_value=FakeKeep())
def test_build_keep_client_reuses_cached_state(_mock_keep, monkeypatch, tmp_path):
    credentials_path = tmp_path / "credentials.json"
    state_path = tmp_path / "state.json"
    state_path.write_text('{"nodes": [1], "version": 1}', encoding="utf-8")

    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))
    monkeypatch.setenv("GOOGLE_STATE_PATH", str(state_path))

    save_credentials("user@example.com", "master-token")
    keep = build_keep_client()

    assert keep.authenticate_calls == [
        ("user@example.com", "master-token", {"nodes": [1], "version": 1})
    ]


@patch("app.keep_client.Keep", return_value=FakeKeepLoginError())
def test_build_keep_client_surfaces_login_errors(_mock_keep, monkeypatch, tmp_path):
    credentials_path = tmp_path / "credentials.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))

    save_credentials("user@example.com", "bad-token")

    with pytest.raises(KeepClientError) as exc:
        build_keep_client()

    assert exc.value.status_code == 401


@patch("app.keep_client.Keep", return_value=FakeKeepUnexpectedError())
def test_build_keep_client_surfaces_unexpected_errors(_mock_keep, monkeypatch, tmp_path):
    credentials_path = tmp_path / "credentials.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))

    save_credentials("user@example.com", "token")

    with pytest.raises(KeepClientError) as exc:
        build_keep_client()

    assert exc.value.status_code == 503


def test_build_keep_client_requires_credentials_file(monkeypatch, tmp_path):
    credentials_path = tmp_path / "missing.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))

    with pytest.raises(KeepClientError) as exc:
        build_keep_client()

    assert exc.value.status_code == 428


def test_save_credentials_and_has_credentials(monkeypatch, tmp_path):
    credentials_path = tmp_path / "credentials.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", str(credentials_path))

    assert has_credentials() is False

    save_credentials(" user@example.com ", " token ")

    assert has_credentials() is True
    payload = json.loads(credentials_path.read_text(encoding="utf-8"))
    assert payload == {"email": "user@example.com", "master_token": "token"}
