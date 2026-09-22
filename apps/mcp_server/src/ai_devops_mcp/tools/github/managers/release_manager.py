# ai_devops_mcp/tools/github/managers/release_manager.py

from ..api.releases import ReleaseAPI


class ReleaseManager:
    """Manage GitHub releases."""

    def __init__(
        self,
        api: ReleaseAPI,
    ) -> None:
        self.api = api

    def get_releases(
        self,
        owner: str,
        repo: str,
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List releases."""

        data = self.api.get_releases(
            owner=owner,
            repo=repo,
            per_page=per_page,
            page=page,
        )

        releases = [
            self._serialize_release(release)
            for release in data
        ]

        return {
            "count": len(releases),
            "releases": releases,
        }

    def get_latest_release(
        self,
        owner: str,
        repo: str,
    ) -> dict:
        """Get latest release."""

        data = self.api.get_latest_release(
            owner=owner,
            repo=repo,
        )

        return self._serialize_release(data)

    def get_release_by_tag(
        self,
        owner: str,
        repo: str,
        tag: str,
    ) -> dict:
        """Get release by tag."""

        data = self.api.get_release_by_tag(
            owner=owner,
            repo=repo,
            tag=tag,
        )

        return self._serialize_release(data)

    @staticmethod
    def _serialize_release(
        data: dict,
    ) -> dict:

        return {
            "id": data["id"],
            "tag_name": data["tag_name"],
            "name": data.get("name") or data["tag_name"],
            "body": data.get("body"),
            "url": data["html_url"],
            "created_at": data["created_at"],
            "published_at": data.get("published_at"),
            "is_draft": data["draft"],
            "is_prerelease": data["prerelease"],
        }