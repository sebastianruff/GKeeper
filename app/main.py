from typing import Any

from flask import Flask, jsonify

from app.keep_client import KeepClientError, build_keep_client


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
            keep = build_keep_client()
        except KeepClientError as exc:
            return jsonify({"error": str(exc)}), exc.status_code

        notes = [_serialize_note(note) for note in keep.all() if not note.trashed]
        return jsonify(notes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
