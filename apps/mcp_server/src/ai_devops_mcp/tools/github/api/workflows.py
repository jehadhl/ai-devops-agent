from typing import Optional

from ..client import GitHubClientProvider
from ..exceptions import GitHubValidationError


class WorkflowAPI:
    """GitHub Actions workflow API endpoints."""

    def __init__(
        self,
        client: GitHubClientProvider,
    ) -> None:
        self.client = client

    def get_workflows(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List workflows in a repository."""

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
            f"/repos/{owner}/{repo}/actions/workflows",
            params={
                "per_page": per_page,
                "page": page,
            },
        )

    def get_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """Get runs for a workflow."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        if not workflow_id:
            raise GitHubValidationError(
                "Workflow ID or filename is required"
            )

        per_page = max(
            1,
            min(per_page, 100),
        )

        page = max(1, page)

        return self.client.request(
            "GET",
            (
                f"/repos/{owner}/{repo}"
                f"/actions/workflows/{workflow_id}/runs"
            ),
            params={
                "per_page": per_page,
                "page": page,
            },
        )

    def trigger_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
        ref: str = "main",
        inputs: Optional[dict] = None,
    ) -> dict | None:
        """Trigger a workflow dispatch."""

        self._validate_repository(
            owner=owner,
            repo=repo,
        )

        if not workflow_id:
            raise GitHubValidationError(
                "Workflow ID or filename is required"
            )

        if not ref:
            raise GitHubValidationError(
                "Git reference is required"
            )

        return self.client.request(
            "POST",
            (
                f"/repos/{owner}/{repo}"
                f"/actions/workflows/{workflow_id}/dispatches"
            ),
            json={
                "ref": ref,
                "inputs": inputs or {},
            },
        )

    @staticmethod
    def _validate_repository(
        owner: str,
        repo: str,
    ) -> None:
        """Validate repository identifiers."""

        if not owner:
            raise GitHubValidationError(
                "Repository owner is required"
            )

        if not repo:
            raise GitHubValidationError(
                "Repository name is required"
            )