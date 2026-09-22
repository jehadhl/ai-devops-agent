# ai_devops_mcp/tools/github/managers/workflow_manager.py

from typing import Optional

from ..api.workflows import WorkflowAPI


class WorkflowManager:
    """Manage GitHub Actions workflows."""

    def __init__(
        self,
        api: WorkflowAPI,
    ) -> None:
        self.api = api

    def list_workflows(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List workflows."""

        data = self.api.get_workflows(
            owner=owner,
            repo=repo,
            per_page=per_page,
            page=page,
        )

        workflows = [
            {
                "id": workflow["id"],
                "name": workflow["name"],
                "path": workflow["path"],
                "state": workflow["state"],
                "url": workflow["html_url"],
                "created_at": workflow["created_at"],
                "updated_at": workflow["updated_at"],
            }
            for workflow in data.get("workflows", [])
        ]

        return {
            "count": len(workflows),
            "workflows": workflows,
        }

    def get_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """Get workflow runs."""

        data = self.api.get_workflow_runs(
            owner=owner,
            repo=repo,
            workflow_id=workflow_id,
            per_page=per_page,
            page=page,
        )

        runs = [
            self._serialize_workflow_run(run)
            for run in data.get("workflow_runs", [])
        ]

        return {
            "count": len(runs),
            "runs": runs,
        }

    def trigger_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: int | str,
        ref: str = "main",
        inputs: Optional[dict] = None,
    ) -> dict:
        """Trigger workflow."""

        result = self.api.trigger_workflow(
            owner=owner,
            repo=repo,
            workflow_id=workflow_id,
            ref=ref,
            inputs=inputs,
        )

        return {
            "triggered": True,
            "workflow_id": workflow_id,
            "ref": ref,
            "result": result,
        }

    @staticmethod
    def _serialize_workflow_run(
        data: dict,
    ) -> dict:
        return {
            "id": data["id"],
            "run_number": data["run_number"],
            "name": data["name"],
            "status": data["status"],
            "conclusion": data.get("conclusion"),
            "branch": data.get("head_branch"),
            "sha": data["head_sha"],
            "url": data["html_url"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
        }