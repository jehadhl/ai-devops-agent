from ..client import GitHubClientProvider
from ..exceptions import GitHubValidationError


class ReleaseAPI:
    """GitHub release API endpoints."""

    def __init__(
        self,
        client: GitHubClientProvider,
    ) -> None:
        self.client = client

    def get_releases(
        self,
        owner: str,
        repo: str,
        per_page: int = 10,
        page: int = 1,
    ) -> list[dict]:
        """List repository releases."""

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
            f"/repos/{owner}/{repo}/releases",
            params={
                "per_page": per_page,
                "page": page,
            },
        )

    def get_latest_release(
        self,
        owner: str,
        repo: str,
    ) -> dict:
        """Get latest published release."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        return self.client.request(
            "GET",
            f"/repos/{owner}/{repo}/releases/latest",
        )

    def get_release_by_tag(
        self,
        owner: str,
        repo: str,
        tag: str,
    ) -> dict:
        """Get release by tag."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        if not tag:
            raise GitHubValidationError(
                "Release tag is required"
            )

        return self.client.request(
            "GET",
            (
                f"/repos/{owner}/{repo}"
                f"/releases/tags/{tag}"
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