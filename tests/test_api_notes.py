from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import create_app


class FakeKeep:
    def __init__(self, notes):
        self._notes = notes

    def all(self):
        return self._notes


def make_note(note_id, *, title="", text="", pinned=False, archived=False, trashed=False, updated=None):
    return SimpleNamespace(
        id=note_id,
        title=title,
        text=text,
        pinned=pinned,
        archived=archived,
        trashed=trashed,
        timestamps=SimpleNamespace(updated=updated),
    )


def test_api_notes_filters_and_sorts_by_default():
    app = create_app()
    client = app.test_client()

    notes = [
        make_note("1", title="visible older", updated=datetime(2024, 1, 1, tzinfo=timezone.utc)),
        make_note("2", title="archived", archived=True, updated=datetime(2025, 1, 1, tzinfo=timezone.utc)),
        make_note("3", title="trashed", trashed=True, updated=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        make_note("4", title="visible newer", updated=datetime(2025, 6, 1, tzinfo=timezone.utc)),
    ]

    with patch("app.main.build_keep_client", return_value=FakeKeep(notes)):
        response = client.get("/api/notes")

    assert response.status_code == 200
    payload = response.get_json()
    assert [note["id"] for note in payload] == ["4", "1"]
    assert set(payload[0].keys()) == {
        "id",
        "title",
        "text",
        "pinned",
        "archived",
        "trashed",
        "updated",
    }


def test_api_notes_can_include_archived_and_trashed():
    app = create_app()
    client = app.test_client()

    notes = [
        make_note("1", archived=True),
        make_note("2", trashed=True),
    ]

    with patch("app.main.build_keep_client", return_value=FakeKeep(notes)):
        response = client.get("/api/notes?include_archived=true&include_trashed=1")

    assert response.status_code == 200
    payload = response.get_json()
    assert [note["id"] for note in payload] == ["1", "2"]
