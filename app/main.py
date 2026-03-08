import os
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

from app.keep_client import KeepClientError, build_keep_client, has_credentials, save_credentials


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_note(note):
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
    def index():
        return send_from_directory(app.static_folder or "static", "index.html")

    @app.get("/api/config")
    def api_config():
        return jsonify({"credentials_configured": has_credentials()})

    @app.post("/api/config")
    def api_save_config():
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "") or "").strip()
        master_token = str(payload.get("master_token", "") or "").strip()

        if not email or not master_token:
            return jsonify({"error": "Email and master token are required."}), 400

        save_credentials(email, master_token)
        return jsonify({"credentials_configured": True})

    @app.get("/api/notes")
    def api_notes():
        include_archived = _parse_bool(request.args.get("include_archived"), default=False)
        include_trashed = _parse_bool(request.args.get("include_trashed"), default=False)

        try:
            keep = build_keep_client()
        except KeepClientError as exc:
            return jsonify({"error": str(exc)}), exc.status_code

        normalized_notes = []
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


def _get_server_port() -> int:
    raw_port = os.getenv("PORT", "5000").strip()
    try:
        port = int(raw_port)
    except ValueError:
        return 5000

    return port if 1 <= port <= 65535 else 5000


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=_get_server_port())
