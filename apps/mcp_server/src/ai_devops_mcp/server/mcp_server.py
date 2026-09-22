import logging
from typing import Callable

from mcp.server.mcpserver import MCPServer

from ai_devops_mcp.core.config import Settings
from ai_devops_mcp.server.context import AppContext

from ai_devops_mcp.tools.docker.registry import register_docker_tools
from ai_devops_mcp.tools.github.registry import register_github_tools


logger = logging.getLogger(__name__)


ToolRegistryFunc = Callable[
    [MCPServer, AppContext, Settings],
    None,
]

TOOL_REGISTRIES: list[
    tuple[str, ToolRegistryFunc]
] = [
    ("docker", register_docker_tools),
    ("github", register_github_tools),
    # Future:
    # ("kubernetes", register_kubernetes_tools),
    # ("aws", register_aws_tools),
]


def create_mcp_server(
    settings: Settings,
) -> tuple[MCPServer, AppContext]:
    """
    Create and configure the MCP server
    with all registered tool providers.
    """

    logger.info(
        "Creating MCP server: %s",
        settings.app_name,
    )

    mcp = MCPServer(
        settings.app_name
    )

    context = AppContext()

    # =========================================================
    # Register providers / tools
    # =========================================================

    for tool_name, registry_func in TOOL_REGISTRIES:
        try:
            logger.info(
                "Registering %s tools...",
                tool_name,
            )

            registry_func(
                mcp=mcp,
                context=context,
                settings=settings,
            )

            logger.info(
                "%s tools registered successfully",
                tool_name,
            )

        except Exception as exc:
            logger.error(
                "Failed to register %s tools: %s",
                tool_name,
                exc,
                exc_info=True,
            )

            if settings.fail_on_tool_registration_error:
                logger.critical(
                    "Failing due to tool registration error"
                )
                raise

            logger.warning(
                "Skipping %s tools due to registration error",
                tool_name,
            )

    logger.info(
        "MCP server created successfully with %d providers",
        context.provider_count(),
    )

    return mcp, context