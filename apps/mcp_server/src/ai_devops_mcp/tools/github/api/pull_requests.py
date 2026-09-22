from typing import Literal

from ..client import GitHubClientProvider
from ..exceptions import GitHubValidationError


PullRequestState = Literal[
    "open",
    "closed",
    "all",
]


class PullRequestAPI:
    """GitHub pull request API endpoints."""

    def __init__(
        self,
        client: GitHubClientProvider,
    ) -> None:
        self.client = client

    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: PullRequestState = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> list[dict]:
        """List pull requests."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        per_page = max(
            1,
            min(per_page, 100),
        )

        page = max(1, page)

        return self.client.request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={
                "state": state,
                "per_page": per_page,
                "page": page,
            },
        )

    def get_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict:
        """Get a single pull request."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        if pull_number <= 0:
            raise GitHubValidationError(
                "Pull request number must be greater than 0"
            )

        return self.client.request(
            "GET",
            (
                f"/repos/{owner}/{repo}"
                f"/pulls/{pull_number}"
            ),
        )

    @staticmethod
    def _validate_repository(
        owner: str,
        repo: str,
    ) -> None:

        if not owner:
            raise GitHubValidationError(
                "Repository owner is required"
            )

        if not repo:
            raise GitHubValidationError(
                "Repository name is required"
            )