import logging
from typing import Any, Callable, Literal, Optional

from mcp.server.mcpserver import MCPServer

from ai_devops_mcp.core.config import Settings
from ai_devops_mcp.server.context import AppContext

from .api import (
    IssueAPI,
    PullRequestAPI,
    ReleaseAPI,
    RepositoryAPI,
    WorkflowAPI,
)
from .client import GitHubClientProvider
from .exceptions import GitHubError
from .managers import (
    IssueManager,
    PullRequestManager,
    ReleaseManager,
    RepositoryManager,
    WorkflowManager,
)

logger = logging.getLogger(__name__)


# =========================================================
# Utilities
# =========================================================

def _execute(
    operation: Callable[..., dict],
    *args: Any,
    **kwargs: Any,
) -> dict:
    """
    Execute a GitHub manager operation and convert
    application exceptions into MCP-friendly responses.
    """

    try:
        result = operation(
            *args,
            **kwargs,
        )

        return {
            "success": True,
            "data": result,
        }

    except GitHubError as exc:
        logger.warning(
            "GitHub operation failed: %s",
            exc.message,
        )

        return {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        }

    except Exception:
        logger.exception(
            "Unexpected error while executing GitHub operation"
        )

        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Unexpected internal error.",
            },
        }


# =========================================================
# Repository Tools
# =========================================================

def _register_repository_tools(
    mcp: MCPServer,
    repositories: RepositoryManager,
) -> None:
    """Register GitHub repository tools."""

    @mcp.tool()
    def github_get_repository(
        owner: str,
        repo: str,
    ) -> dict:
        """Get information about a GitHub repository."""

        return _execute(
            repositories.get_repository,
            owner=owner,
            repo=repo,
        )

    @mcp.tool()
    def github_list_repositories(
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List repositories accessible to authenticated user."""

        return _execute(
            repositories.list_authenticated_repositories,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_list_organization_repositories(
        organization: str,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List repositories belonging to a GitHub organization."""

        return _execute(
            repositories.list_organization_repositories,
            organization=organization,
            per_page=per_page,
            page=page,
        )


# =========================================================
# Workflow Tools
# =========================================================

def _register_workflow_tools(
    mcp: MCPServer,
    workflows: WorkflowManager,
) -> None:
    """Register GitHub workflow tools."""

    @mcp.tool()
    def github_list_workflows(
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> dict:
        """List GitHub Actions workflows."""

        return _execute(
            workflows.list_workflows,
            owner=owner,
            repo=repo,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_get_workflow_runs(
        owner: str,
        repo: str,
        workflow_id: str,
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """Get runs for a GitHub Actions workflow."""

        return _execute(
            workflows.get_workflow_runs,
            owner=owner,
            repo=repo,
            workflow_id=workflow_id,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_trigger_workflow(
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: Optional[dict] = None,
    ) -> dict:
        """Trigger a GitHub Actions workflow."""

        return _execute(
            workflows.trigger_workflow,
            owner=owner,
            repo=repo,
            workflow_id=workflow_id,
            ref=ref,
            inputs=inputs,
        )


# =========================================================
# Pull Request Tools
# =========================================================

def _register_pull_request_tools(
    mcp: MCPServer,
    pull_requests: PullRequestManager,
) -> None:
    """Register GitHub pull request tools."""

    @mcp.tool()
    def github_get_pull_requests(
        owner: str,
        repo: str,
        state: Literal[
            "open",
            "closed",
            "all",
        ] = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List pull requests."""

        return _execute(
            pull_requests.get_pull_requests,
            owner=owner,
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_get_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict:
        """Get a specific pull request."""

        return _execute(
            pull_requests.get_pull_request,
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )


# =========================================================
# Issue Tools
# =========================================================

def _register_issue_tools(
    mcp: MCPServer,
    issues: IssueManager,
) -> None:
    """Register GitHub issue tools."""

    @mcp.tool()
    def github_get_issues(
        owner: str,
        repo: str,
        state: Literal[
            "open",
            "closed",
            "all",
        ] = "open",
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List GitHub issues."""

        return _execute(
            issues.get_issues,
            owner=owner,
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_get_issue(
        owner: str,
        repo: str,
        issue_number: int,
    ) -> dict:
        """Get a specific GitHub issue."""

        return _execute(
            issues.get_issue,
            owner=owner,
            repo=repo,
            issue_number=issue_number,
        )


# =========================================================
# Release Tools
# =========================================================

def _register_release_tools(
    mcp: MCPServer,
    releases: ReleaseManager,
) -> None:
    """Register GitHub release tools."""

    @mcp.tool()
    def github_get_releases(
        owner: str,
        repo: str,
        per_page: int = 10,
        page: int = 1,
    ) -> dict:
        """List GitHub releases."""

        return _execute(
            releases.get_releases,
            owner=owner,
            repo=repo,
            per_page=per_page,
            page=page,
        )

    @mcp.tool()
    def github_get_latest_release(
        owner: str,
        repo: str,
    ) -> dict:
        """Get latest published GitHub release."""

        return _execute(
            releases.get_latest_release,
            owner=owner,
            repo=repo,
        )

    @mcp.tool()
    def github_get_release_by_tag(
        owner: str,
        repo: str,
        tag: str,
    ) -> dict:
        """Get GitHub release by tag."""

        return _execute(
            releases.get_release_by_tag,
            owner=owner,
            repo=repo,
            tag=tag,
        )


# =========================================================
# Main Registration
# =========================================================

def register_github_tools(
    mcp: MCPServer,
    context: AppContext,
    settings: Settings,
) -> None:
    """Initialize GitHub provider and register all GitHub tools."""

    logger.info(
        "Initializing GitHub provider..."
    )

    # =========================================================
    # Client
    # =========================================================

    github_client = GitHubClientProvider(
        token=settings.github_token,
        base_url=settings.github_api_url,
        timeout=settings.github_timeout,
    )

    context.register_provider(
        "github",
        github_client,
    )

    logger.info(
        "GitHub client initialized successfully"
    )

    # =========================================================
    # APIs
    # =========================================================

    repository_api = RepositoryAPI(
        github_client
    )

    workflow_api = WorkflowAPI(
        github_client
    )

    issue_api = IssueAPI(
        github_client
    )

    pull_request_api = PullRequestAPI(
        github_client
    )

    release_api = ReleaseAPI(
        github_client
    )

    # =========================================================
    # Managers
    # =========================================================

    repositories = RepositoryManager(
        repository_api
    )

    workflows = WorkflowManager(
        workflow_api
    )

    issues = IssueManager(
        issue_api
    )

    pull_requests = PullRequestManager(
        pull_request_api
    )

    releases = ReleaseManager(
        release_api
    )

    # =========================================================
    # Register Tools
    # =========================================================

    logger.info(
        "Registering GitHub repository tools..."
    )
    _register_repository_tools(
        mcp,
        repositories,
    )

    logger.info(
        "Registering GitHub workflow tools..."
    )
    _register_workflow_tools(
        mcp,
        workflows,
    )

    logger.info(
        "Registering GitHub pull request tools..."
    )
    _register_pull_request_tools(
        mcp,
        pull_requests,
    )

    logger.info(
        "Registering GitHub issue tools..."
    )
    _register_issue_tools(
        mcp,
        issues,
    )

    logger.info(
        "Registering GitHub release tools..."
    )
    _register_release_tools(
        mcp,
        releases,
    )

    logger.info(
        "All GitHub tools registered successfully"
    )