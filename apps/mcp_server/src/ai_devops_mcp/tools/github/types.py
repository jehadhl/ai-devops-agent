from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """GitHub workflow status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REQUESTED = "requested"
    WAITING = "waiting"


class WorkflowConclusion(str, Enum):
    """GitHub workflow conclusion."""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    STALE = "stale"


class Repository(BaseModel):
    """GitHub repository information."""
    id: int
    name: str
    full_name: str
    owner: str
    description: Optional[str] = None
    url: str
    stars: int
    forks: int
    watchers: int
    language: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkflowRun(BaseModel):
    """GitHub workflow run."""
    id: int
    run_number: int
    name: str
    status: WorkflowStatus
    conclusion: Optional[WorkflowConclusion] = None
    created_at: datetime
    updated_at: datetime
    head_branch: str
    head_sha: str
    url: str


class PullRequestState(str, Enum):
    """Pull request state."""
    OPEN = "open"
    CLOSED = "closed"


class PullRequest(BaseModel):
    """GitHub pull request."""
    id: int
    number: int
    title: str
    description: Optional[str] = None
    state: PullRequestState
    author: str
    created_at: datetime
    updated_at: datetime
    url: str
    head_branch: str
    base_branch: str


class IssueState(str, Enum):
    """Issue state."""
    OPEN = "open"
    CLOSED = "closed"


class Issue(BaseModel):
    """GitHub issue."""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: IssueState
    author: str
    created_at: datetime
    updated_at: datetime
    url: str
    labels: list[str] = Field(default_factory=list)


class Release(BaseModel):
    """GitHub release."""
    id: int
    tag_name: str
    name: str
    body: Optional[str] = None
    created_at: datetime
    published_at: Optional[datetime] = None
    url: str
    is_draft: bool
    is_prerelease: bool


class CommitInfo(BaseModel):
    """Git commit information."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    url: str