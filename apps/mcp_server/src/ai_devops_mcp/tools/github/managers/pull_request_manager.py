from ..api.pull_requests import (
    PullRequestAPI,
    PullRequestState,
)


class PullRequestManager:
    """Manage GitHub pull requests."""

    def __init__(
        self,
        api: PullRequestAPI,
    ) -> None:
        self.api = api

    def get_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict:
        """Get a single pull request."""

        data = self.api.get_pull_request(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )

        return self._serialize_pull_request(data)

    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: PullRequestState = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List pull requests."""

        data = self.api.get_pull_requests(
            owner=owner,
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
        )

        pull_requests = [
            self._serialize_pull_request(pr)
            for pr in data
        ]

        return {
            "count": len(pull_requests),
            "pull_requests": pull_requests,
        }

    @staticmethod
    def _serialize_pull_request(
        data: dict,
    ) -> dict:
        """Convert GitHub pull request JSON to MCP-friendly dict."""

        return {
            "id": data["id"],
            "number": data["number"],
            "title": data["title"],
            "description": data.get("body"),
            "state": data["state"],
            "author": data["user"]["login"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "url": data["html_url"],
            "head_branch": data["head"]["ref"],
            "base_branch": data["base"]["ref"],
        }