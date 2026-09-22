from ..api.issues import (
    IssueAPI,
    IssueState,
)


class IssueManager:
    """Manage GitHub issues."""

    def __init__(
        self,
        api: IssueAPI,
    ) -> None:
        self.api = api

    def get_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> dict:
        """Get a single GitHub issue."""

        data = self.api.get_issue(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
        )

        return self._serialize_issue(data)

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: IssueState = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List GitHub issues."""

        data = self.api.get_issues(
            owner=owner,
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
        )

        issues = [
            self._serialize_issue(issue)
            for issue in data
        ]

        return {
            "count": len(issues),
            "issues": issues,
        }

    @staticmethod
    def _serialize_issue(
        data: dict,
    ) -> dict:
        """Convert GitHub issue JSON to MCP-friendly dict."""

        labels: list[str] = []

        for label in data.get("labels", []):
            if isinstance(label, dict):
                name = label.get("name")

                if name:
                    labels.append(name)

            elif isinstance(label, str):
                labels.append(label)

        return {
            "id": data["id"],
            "number": data["number"],
            "title": data["title"],
            "body": data.get("body"),
            "state": data["state"],
            "author": data["user"]["login"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "url": data["html_url"],
            "labels": labels,
        }