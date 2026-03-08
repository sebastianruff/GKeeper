import os
from typing import Any

from flask import Flask, jsonify
from gkeepapi import Keep


def _build_keep_client() -> Keep:
    """Authenticate a Keep client from environment variables."""
    email = os.environ.get("GKEEP_EMAIL")
    password = os.environ.get("GKEEP_PASSWORD")
    master_token = os.environ.get("GKEEP_MASTER_TOKEN")

    keep = Keep()

    if master_token:
        keep.resume(email or "", master_token)
    elif email and password:
        keep.login(email, password)
    else:
        raise RuntimeError(
            "Missing credentials. Set GKEEP_MASTER_TOKEN (optional with GKEEP_EMAIL) "
            "or set GKEEP_EMAIL + GKEEP_PASSWORD."
        )

    return keep


def _serialize_note(note: Any) -> dict[str, Any]:
    return {
        "id": note.id,
        "title": note.title,
        "text": note.text,
        "trashed": note.trashed,
        "pinned": note.pinned,
        "archived": note.archived,
        "color": str(note.color),
        "updated": note.timestamps.updated.isoformat() if note.timestamps.updated else None,
    }


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return """
        <!doctype html>
        <html lang=\"de\">
          <head>
            <meta charset=\"utf-8\">
            <title>GKeeper</title>
          </head>
          <body>
            <h1>GKeeper</h1>
            <p>API-Endpunkt: <code>/api/notes</code></p>
          </body>
        </html>
        """

    @app.get("/api/notes")
    def api_notes():
        try:
            keep = _build_keep_client()
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 503

        notes = [_serialize_note(note) for note in keep.all() if not note.trashed]
        return jsonify(notes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
