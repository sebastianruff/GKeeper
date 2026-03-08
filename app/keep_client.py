import logging
import os

from gkeepapi import Keep, exception

logger = logging.getLogger(__name__)


class KeepClientError(Exception):
    """Domain error for Keep client initialization."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code



def build_keep_client() -> Keep:
    """Create and authenticate a Keep client from environment variables."""
    email = os.environ.get("KEEP_EMAIL")
    app_password = os.environ.get("KEEP_APP_PASSWORD")

    if not email or not app_password:
        logger.error(
            "Google Keep credentials are not configured. Expected KEEP_EMAIL and KEEP_APP_PASSWORD."
        )
        raise KeepClientError("Keep service unavailable", 503)

    keep = Keep()

    try:
        keep.login(email, app_password)
    except exception.LoginException:
        logger.warning("Google Keep login failed due to invalid credentials.")
        raise KeepClientError("Keep authentication failed", 401) from None
    except Exception:
        logger.exception("Unexpected error while logging into Google Keep.")
        raise KeepClientError("Keep service unavailable", 503) from None

    return keep
