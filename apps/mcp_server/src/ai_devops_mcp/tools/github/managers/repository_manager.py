from ..api.repositories import RepositoryAPI


class RepositoryManager:
    """Manage GitHub repositories."""

    def __init__(
        self,
        api: RepositoryAPI,
    ) -> None:
        self.api = api

    def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict:
        """Get repository information."""

        data = self.api.get_repository(
            owner=owner,
            repo=repo,
        )

        return self._serialize_repository(data)

    def list_authenticated_repositories(
        self,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List repositories accessible to authenticated user."""

        data = self.api.list_authenticated_repositories(
            per_page=per_page,
            page=page,
        )

        repositories = [
            self._serialize_repository(repo)
            for repo in data
        ]

        return {
            "count": len(repositories),
            "repositories": repositories,
        }

    def list_organization_repositories(
        self,
        organization: str,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List organization repositories."""

        data = self.api.list_organization_repositories(
            organization=organization,
            per_page=per_page,
            page=page,
        )

        repositories = [
            self._serialize_repository(repo)
            for repo in data
        ]

        return {
            "organization": organization,
            "count": len(repositories),
            "repositories": repositories,
        }

    @staticmethod
    def _serialize_repository(
        data: dict,
    ) -> dict:
        """Convert GitHub repository response into MCP-friendly data."""

        return {
            "id": data["id"],
            "name": data["name"],
            "full_name": data["full_name"],
            "owner": data["owner"]["login"],
            "description": data.get("description"),
            "url": data["html_url"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "watchers": data["watchers_count"],
            "language": data.get("language"),
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
        }