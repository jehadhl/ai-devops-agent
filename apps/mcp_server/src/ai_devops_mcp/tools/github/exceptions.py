from typing import Optional


class GitHubError(Exception):
    """Base GitHub error."""

    def __init__(
        self,
        code: str,
        message: str,
    ) -> None:
        self.code = code
        self.message = message

        super().__init__(message)


class GitHubAuthenticationError(GitHubError):
    """GitHub authentication error."""

    def __init__(
        self,
        message: str = "Invalid GitHub token",
    ) -> None:
        super().__init__(
            "AUTH_ERROR",
            message,
        )


class GitHubNotFoundError(GitHubError):
    """GitHub resource not found error."""

    def __init__(
        self,
        resource: str = "Resource",
    ) -> None:
        super().__init__(
            "NOT_FOUND",
            f"{resource} not found",
        )


class GitHubValidationError(GitHubError):
    """GitHub validation error."""

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            "VALIDATION_ERROR",
            message,
        )


class GitHubRateLimitError(GitHubError):
    """GitHub API rate limit error."""

    def __init__(
        self,
        message: str = "GitHub API rate limit exceeded",
        retry_after: Optional[str] = None,
        reset_at: Optional[str] = None,
    ) -> None:
        self.retry_after = retry_after
        self.reset_at = reset_at

        super().__init__(
            "RATE_LIMIT",
            message,
        )


class GitHubPermissionError(GitHubError):
    """GitHub permission denied error."""

    def __init__(
        self,
        message: str = "GitHub API permission denied",
    ) -> None:
        super().__init__(
            "PERMISSION_DENIED",
            message,
        )


class GitHubAPIError(GitHubError):
    """General GitHub API error."""

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            "API_ERROR",
            message,
        )