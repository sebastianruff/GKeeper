from datetime import datetime
from typing import Any

from flask import Flask, jsonify, request

from app.keep_client import KeepClientError, build_keep_client


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_note(note: Any) -> dict[str, Any]:
    updated = getattr(getattr(note, "timestamps", None), "updated", None)
    updated_iso = updated.isoformat() if isinstance(updated, datetime) else None

    return {
        "id": str(getattr(note, "id", "")),
        "title": str(getattr(note, "title", "") or ""),
        "text": str(getattr(note, "text", "") or ""),
        "pinned": bool(getattr(note, "pinned", False)),
        "archived": bool(getattr(note, "archived", False)),
        "trashed": bool(getattr(note, "trashed", False)),
        "updated": updated_iso,
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
        include_archived = _parse_bool(request.args.get("include_archived"), default=False)
        include_trashed = _parse_bool(request.args.get("include_trashed"), default=False)

        try:
            keep = build_keep_client()
        except KeepClientError as exc:
            return jsonify({"error": str(exc)}), exc.status_code

        normalized_notes: list[dict[str, Any]] = []
        for note in keep.all():
            normalized_note = _normalize_note(note)

            if not include_archived and normalized_note["archived"]:
                continue
            if not include_trashed and normalized_note["trashed"]:
                continue

            normalized_notes.append(normalized_note)

        normalized_notes.sort(key=lambda note: note["updated"] or "", reverse=True)
        return jsonify(normalized_notes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
