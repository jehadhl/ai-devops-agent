import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    app_name: str = "AI DevOps MCP"
    log_level: str = "INFO"

    docker_retry_attempts: int = 3
    docker_retry_delay: float = 1.0

    fail_on_tool_registration_error: bool = False

    github_token: str = ""
    github_api_url: str = "https://api.github.com"
    github_timeout: float = 10.0


def get_settings() -> Settings:
    """Load application settings from environment variables."""

    return Settings(
        app_name=os.getenv(
            "APP_NAME",
            "AI DevOps MCP",
        ),
        log_level=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ).upper(),
        docker_retry_attempts=int(
            os.getenv(
                "DOCKER_RETRY_ATTEMPTS",
                "3",
            )
        ),
        docker_retry_delay=float(
            os.getenv(
                "DOCKER_RETRY_DELAY",
                "1.0",
            )
        ),
        fail_on_tool_registration_error=env_bool(
            "FAIL_ON_TOOL_REGISTRATION_ERROR",
            False,
        ),
        github_api_url=os.getenv(
            "GITHUB_API_URL",
            "https://api.github.com",
        ),
        github_timeout=float(
            os.getenv(
                "GITHUB_TIMEOUT",
                "10",
            )
        ),
        github_token=os.getenv(
            "GITHUB_TOKEN",
            "",
        ),
    )
