
from typing import Literal

from ..client import GitHubClientProvider
from ..exceptions import GitHubValidationError


RepositoryVisibility = Literal[
    "all",
    "public",
    "private",
]


class RepositoryAPI:
    """GitHub repository API endpoints."""

    def __init__(
        self,
        client: GitHubClientProvider,
    ) -> None:
        self.client = client

    def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict:
        """Get a repository."""

        if not owner:
            raise GitHubValidationError(
                "Repository owner is required"
            )

        if not repo:
            raise GitHubValidationError(
                "Repository name is required"
            )

        return self.client.request(
            "GET",
            f"/repos/{owner}/{repo}",
        )

    def list_authenticated_repositories(
        self,
        per_page: int = 30,
        page: int = 1,
        visibility: RepositoryVisibility = "all",
    ) -> list[dict]:
        """List repositories accessible to authenticated user."""

        per_page = max(
            1,
            min(per_page, 100),
        )

        page = max(1, page)

        return self.client.request(
            "GET",
            "/user/repos",
            params={
                "per_page": per_page,
                "page": page,
                "visibility": visibility,
            },
        )

    def list_organization_repositories(
        self,
        organization: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict]:
        """List repositories for an organization."""

        if not organization:
            raise GitHubValidationError(
                "GitHub organization is required"
            )

        per_page = max(
            1,
            min(per_page, 100),
        )

        page = max(1, page)

        return self.client.request(
            "GET",
            f"/orgs/{organization}/repos",
            params={
                "per_page": per_page,
                "page": page,
            },
        )