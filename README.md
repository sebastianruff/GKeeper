# GKeeper

A web app for Google Keep based on kiwiz/gkeepapi.

## Prerequisites

- A Google account with **2-factor authentication (2FA)** enabled.
- An **app password** created for that account (not your regular Google password).

## API

### `GET /api/notes`

Returns notes in a small, stable JSON schema:

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

Default behavior:

- Archived notes are **filtered out** by default.
- Trashed notes (`trashed`) are **filtered out** by default.
- The result list is sorted by `updated` in **descending** order (newest first).

Optional query parameters:

- `include_archived=true` → include archived notes as well.
- `include_trashed=true` → include trashed notes as well.

## Development

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest -q
```

## Docker

1. Prepare environment variables:

   ```bash
   cp .env.example .env
   ```

   Then set `KEEP_EMAIL` and `KEEP_APP_PASSWORD` in `.env`.

2. Start the container:

   ```bash
   docker compose up
   ```

3. Open in your browser:

   ```text
   http://localhost:5000
   ```

## Current Scope

The current version is **read-only**. Creating, editing, and deleting notes are not supported yet.

## Common Issues

- **Wrong app password:** Google Keep login fails even when the email address is correct.
- **Login fails:** Common causes are missing 2FA, an expired/revoked app password, or typos in `KEEP_EMAIL` or `KEEP_APP_PASSWORD`.
