# ai_devops_mcp/tools/github/client.py

import logging
from typing import Any

import requests

from .exceptions import (
    GitHubAPIError,
    GitHubAuthenticationError,
    GitHubNotFoundError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubValidationError,
)

logger = logging.getLogger(__name__)


class GitHubClientProvider:
    """Low-level GitHub HTTP client provider."""

    def __init__(
        self,
        token: str,
        base_url: str,
        timeout: float,
    ) -> None:
        """
        Initialize GitHub HTTP client.

        Args:
            token: GitHub authentication token.
            base_url: GitHub API base URL.
            timeout: HTTP request timeout in seconds.
        """

        if not token:
            raise GitHubAuthenticationError(
                "GitHub token is required"
            )

        if not base_url:
            raise GitHubValidationError(
                "GitHub API base URL is required"
            )

        if timeout <= 0:
            raise GitHubValidationError(
                "GitHub timeout must be greater than 0"
            )

        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = self._create_session()

        logger.info(
            "GitHub client initialized for API: %s",
            self.base_url,
        )

    # =========================================================
    # Session
    # =========================================================

    def _create_session(self) -> requests.Session:
        """Create authenticated GitHub HTTP session."""

        session = requests.Session()

        session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "OpsKraken",
            }
        )

        return session

    # =========================================================
    # Request
    # =========================================================

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Execute GitHub API request."""

        url = f"{self.base_url}/{path.lstrip('/')}"

        logger.debug(
            "GitHub request: %s %s",
            method.upper(),
            url,
        )

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                timeout=self.timeout,
                **kwargs,
            )

        except requests.Timeout as exc:
            raise GitHubAPIError(
                f"GitHub request timed out after "
                f"{self.timeout} seconds"
            ) from exc

        except requests.RequestException as exc:
            raise GitHubAPIError(
                f"GitHub request failed: {exc}"
            ) from exc

        return self._handle_response(response)

    # =========================================================
    # Response Handling
    # =========================================================

    def _handle_response(
        self,
        response: requests.Response,
    ) -> Any:
        """Handle GitHub API response and map errors."""

        status_code = response.status_code

        # Authentication
        if status_code == 401:
            raise GitHubAuthenticationError()

        # Not Found
        if status_code == 404:
            raise GitHubNotFoundError()

        # Rate Limit / Permission
        if status_code in (403, 429):
            remaining = response.headers.get(
                "X-RateLimit-Remaining"
            )

            retry_after = response.headers.get(
                "Retry-After"
            )

            reset_at = response.headers.get(
                "X-RateLimit-Reset"
            )

            try:
                error_data = response.json()
                message = (
                    error_data
                    .get("message", "")
                    .lower()
                )

            except ValueError:
                message = ""

            is_rate_limit = (
                status_code == 429
                or remaining == "0"
                or retry_after is not None
                or "rate limit" in message
            )

            if is_rate_limit:
                raise GitHubRateLimitError(
                    (
                        "GitHub API rate limit exceeded. "
                        f"Retry-After="
                        f"{retry_after or 'unknown'}, "
                        f"Reset-At="
                        f"{reset_at or 'unknown'}"
                    )
                )

            raise GitHubPermissionError()

        # Validation
        if status_code == 422:
            raise GitHubValidationError(
                f"GitHub validation failed: "
                f"{response.text}"
            )

        # Other errors
        if not response.ok:
            raise GitHubAPIError(
                (
                    f"GitHub API error "
                    f"{status_code}: "
                    f"{response.text}"
                )
            )

        # No Content
        if status_code == 204:
            return None

        if not response.content:
            return None

        # JSON
        try:
            return response.json()

        except ValueError as exc:
            raise GitHubAPIError(
                "GitHub API returned invalid JSON"
            ) from exc

    # =========================================================
    # Lifecycle
    # =========================================================

    def close(self) -> None:
        """Close GitHub HTTP session."""

        self.session.close()

        logger.info(
            "GitHub client closed"
        )