# GKeeper

A web app for Google Keep based on kiwiz/gkeepapi.

GitHub repository: `https://github.com/sebastianruff/GKeeper`

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
   export GKEEPER_IMAGE=ghcr.io/sebastianruff/gkeeper:latest
   ```

   If not set, Compose uses `ghcr.io/sebastianruff/gkeeper:latest` by default.

2. (Optional) choose a custom host port (default: `5000`):

   ```bash
   export GKEEPER_HOST_PORT=5001
   ```

3. Pull and start the container:

   ```bash
   docker compose up
   ```

4. Open in your browser:

   ```text
   http://localhost:${GKEEPER_HOST_PORT:-5000}
   ```

   > Avoid Chrome unsafe ports like `6000` (`ERR_UNSAFE_PORT`). Use a different host port such as `5000`, `5001`, or `8080`.

## Docker Compose example

Use this as a minimal `compose.yaml` example:

```yaml
services:
  gkeeper:
    image: ghcr.io/sebastianruff/gkeeper:latest
    ports:
      - "${GKEEPER_HOST_PORT:-5000}:5000"
    environment:
      GOOGLE_CREDENTIALS_PATH: /data/gkeep_credentials.json
      GOOGLE_STATE_PATH: /data/gkeep_state.json
    volumes:
      - ./data:/data
    restart: unless-stopped
```

> The first time you open the app, enter your Google email + master token in the setup form.
> They will be persisted in `./data/gkeep_credentials.json` with this example.


If you need to change the container-internal port as well, set `PORT` and map accordingly:

```yaml
services:
  gkeeper:
    environment:
      PORT: 5100
    ports:
      - "5001:5100"
```

## Publish the GitHub Package (maintainers)

The image is published to GitHub Container Registry (GHCR) via `.github/workflows/publish-package.yml`.

- Automatic publish on:
  - pushes to `main`
  - tags starting with `v` (for example `v1.0.0`)
- Manual publish via **Actions → Publish Docker package → Run workflow**

Published image name:

```text
ghcr.io/sebastianruff/gkeeper
```

## Current Scope

The current version is **read-only**. Creating, editing, and deleting notes are not supported yet.

## Common Issues

- **Authentication fails:** Most often caused by an invalid/revoked master token or wrong email/token submitted in the setup form.
- **Slow first startup:** The initial sync can take a while. Keep `GOOGLE_STATE_PATH` persisted to speed up subsequent starts.
