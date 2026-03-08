import json
import logging
import os
from pathlib import Path
from typing import Any

from gkeepapi import Keep, exception

logger = logging.getLogger(__name__)


class KeepClientError(Exception):
    """Domain error for Keep client initialization."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def _load_state(state_path: Path) -> dict[str, Any] | None:
    if not state_path.exists():
        return None

    try:
        with state_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        logger.warning("Failed to read Keep state cache from %s.", state_path)
        return None

    if not isinstance(data, dict):
        logger.warning("Keep state cache in %s is not a JSON object.", state_path)
        return None

    return data


def _save_state(keep: Keep, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_data = keep.dump()

    with state_path.open("w", encoding="utf-8") as file:
        json.dump(state_data, file)


def build_keep_client() -> Keep:
    """Create and authenticate a Keep client from environment variables."""
    email = os.environ.get("GOOGLE_EMAIL")
    master_token = os.environ.get("GOOGLE_MASTER_TOKEN")
    state_path = Path(os.environ.get("GOOGLE_STATE_PATH", ".cache/gkeep_state.json"))

    if not email or not master_token:
        logger.error(
            "Google Keep credentials are not configured. Expected GOOGLE_EMAIL and GOOGLE_MASTER_TOKEN."
        )
        raise KeepClientError("Keep service unavailable", 503)

    keep = Keep()
    state = _load_state(state_path)

    try:
        keep.authenticate(email, master_token, state=state)
    except exception.LoginException:
        logger.warning("Google Keep authentication failed due to invalid credentials.")
        raise KeepClientError("Keep authentication failed", 401) from None
    except Exception:
        logger.exception("Unexpected error while authenticating with Google Keep.")
        raise KeepClientError("Keep service unavailable", 503) from None

    try:
        _save_state(keep, state_path)
    except OSError:
        logger.warning("Failed to write Keep state cache to %s.", state_path)

    return keep
