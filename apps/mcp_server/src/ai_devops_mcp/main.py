import logging
import sys

from ai_devops_mcp.core.config import get_settings
from ai_devops_mcp.core.logging import configure_logging
from ai_devops_mcp.server.mcp_server import create_mcp_server

logger = logging.getLogger(__name__)


def main() -> None:
    """Application entry point."""

    context = None

    try:
        settings = get_settings()
        configure_logging(level=settings.log_level)

        logger.info("Starting %s", settings.app_name)

        mcp, context = create_mcp_server(settings=settings)

        logger.info("MCP server ready, starting event loop...")
        mcp.run()

    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
        sys.exit(0)

    except Exception as exc:
        logger.error("Fatal error: %s", exc, exc_info=True)
        sys.exit(1)

    finally:
        if context is not None:
            context.close()
            logger.info("MCP server shutdown complete")


if __name__ == "__main__":
    main()