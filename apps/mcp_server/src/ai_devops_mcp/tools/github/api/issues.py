from typing import Literal

from ..client import GitHubClientProvider
from ..exceptions import GitHubValidationError


IssueState = Literal[
    "open",
    "closed",
    "all",
]


class IssueAPI:
    """GitHub issue API endpoints."""

    def __init__(
        self,
        client: GitHubClientProvider,
    ) -> None:
        self.client = client

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: IssueState = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> list[dict]:
        """List repository issues excluding pull requests."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        per_page = max(
            1,
            min(per_page, 100),
        )

        page = max(1, page)

        data = self.client.request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": state,
                "per_page": per_page,
                "page": page,
            },
        )

        return [
            issue
            for issue in data
            if "pull_request" not in issue
        ]

    def get_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> dict:
        """Get a single repository issue."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        if issue_number <= 0:
            raise GitHubValidationError(
                "Issue number must be greater than 0"
            )

        return self.client.request(
            "GET",
            (
                f"/repos/{owner}/{repo}"
                f"/issues/{issue_number}"
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