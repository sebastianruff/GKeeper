# GKeeper

A web app for Google Keep based on kiwiz/gkeepapi.

## Prerequisites

- A Google account with **2-factor authentication (2FA)** enabled.
- A **Google master token** for that account (used by `gkeepapi.authenticate`).

## Authentication Setup

This project uses `Keep.authenticate(email, master_token)` instead of the deprecated `Keep.login(...)` flow.

To get a master token, follow the `gpsoauth` alternative flow linked from the gkeepapi docs:
<https://github.com/simon-weber/gpsoauth#alternative-flow>

### Optional state cache

The app stores Keep sync state in `KEEP_STATE_PATH` (default: `.cache/gkeep_state.json`) and reuses it on next startup.
This reduces full-sync overhead and follows the gkeepapi recommendation to cache state between runs.

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

   Then set `KEEP_EMAIL` and `KEEP_MASTER_TOKEN` in `.env`.

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

- **Authentication fails:** Most often caused by an invalid/revoked master token or typos in `KEEP_EMAIL` / `KEEP_MASTER_TOKEN`.
- **Slow first startup:** The initial sync can take a while. Keep `KEEP_STATE_PATH` persisted to speed up subsequent starts.
