# GKeeper

A web app for Google Keep based on kiwiz/gkeepapi.

## Prerequisites

- A Google account with **2-factor authentication (2FA)** enabled.
- A **Google master token** for that account (used by `gkeepapi.authenticate`).

## Authentication Setup

This project uses `Keep.authenticate(email, master_token)` instead of the deprecated `Keep.login(...)` flow.

When you open the web app without saved credentials, a setup form is shown automatically.
The form includes a step-by-step guide to create a Google Master Token and asks for:

- Google email
- Google master token

The credentials are stored in `GOOGLE_CREDENTIALS_PATH` (default: `.cache/gkeep_credentials.json`).

### Optional state cache

The app stores Keep sync state in `GOOGLE_STATE_PATH` (default: `.cache/gkeep_state.json`) and reuses it on next startup.
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

## Docker (run from GitHub Package)

1. (Optional) set a custom image tag:

   ```bash
   export GKEEPER_IMAGE=ghcr.io/<github-user-or-org>/gkeeper:latest
   ```

   If not set, Compose uses `ghcr.io/your-github-user/gkeeper:latest` by default.

2. Pull and start the container:

   ```bash
   docker compose up
   ```

3. Open in your browser:

   ```text
   http://localhost:5000
   ```

## Publish the GitHub Package (maintainers)

The image is published to GitHub Container Registry (GHCR) via `.github/workflows/publish-package.yml`.

- Automatic publish on:
  - pushes to `main`
  - tags starting with `v` (for example `v1.0.0`)
- Manual publish via **Actions → Publish Docker package → Run workflow**

Published image name:

```text
ghcr.io/<repository_owner>/gkeeper
```

## Current Scope

The current version is **read-only**. Creating, editing, and deleting notes are not supported yet.

## Common Issues

- **Authentication fails:** Most often caused by an invalid/revoked master token or wrong email/token submitted in the setup form.
- **Slow first startup:** The initial sync can take a while. Keep `GOOGLE_STATE_PATH` persisted to speed up subsequent starts.
