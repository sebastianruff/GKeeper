# GKeeper

A web app for Google Keep based on kiwiz/gkeepapi.

## API

### `GET /api/notes`

Liefert Notizen in einem kleinen, stabilen JSON-Schema:

```json
[
  {
    "id": "...",
    "title": "...",
    "text": "...",
    "pinned": false,
    "archived": false,
    "trashed": false,
    "updated": "2026-01-13T09:22:30.123456+00:00"
  }
]
```

Standardverhalten:

- Archivierte Notizen werden standardmäßig **ausgefiltert**.
- Gelöschte Notizen (`trashed`) werden standardmäßig **ausgefiltert**.
- Ergebnisliste ist nach `updated` **absteigend** sortiert (neueste zuerst).

Optionale Query-Parameter:

- `include_archived=true` → archivierte Notizen zusätzlich einschließen.
- `include_trashed=true` → gelöschte Notizen zusätzlich einschließen.

## Entwicklung

Dependencies installieren:

```bash
pip install -r requirements-dev.txt
```

Tests ausführen:

```bash
pytest -q
```

## Docker

1. Umgebungsvariablen vorbereiten:

   ```bash
   cp .env.example .env
   ```

   Danach `KEEP_EMAIL` und `KEEP_APP_PASSWORD` in `.env` setzen.

2. Container starten:

   ```bash
   docker compose up --build
   ```

Die App ist dann unter `http://localhost:5000` erreichbar.
