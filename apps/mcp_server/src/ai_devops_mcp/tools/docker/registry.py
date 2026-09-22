import logging
from typing import Any, Callable

from mcp.server.mcpserver import MCPServer

from ai_devops_mcp.core.config import Settings
from ai_devops_mcp.server.context import AppContext

from .client import DockerClientProvider
from .containers import ContainerManager
from .images import ImageManager
from .logs import LogsManager
from .networks import NetworkManager
from .volumes import VolumeManager
from .exceptions import DockerError, DockerValidationError

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
    Execute a Docker manager operation and convert
    application exceptions into MCP-friendly responses.
    """
    try:
        result = operation(*args, **kwargs)
        return {
            "success": True,
            "data": result,
        }

    except DockerError as exc:
        logger.warning("Docker operation failed: %s", exc.message)
        return {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        }

    except Exception:
        logger.exception("Unexpected error while executing Docker operation")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Unexpected internal error.",
            },
        }


def _require_confirmation(confirmed: bool, operation: str) -> None:
    """Require explicit confirmation before destructive operations."""
    if not confirmed:
        raise DockerValidationError(
            f"Operation '{operation}' requires explicit confirmation."
        )


# =========================================================
# Container Tools
# =========================================================

def _register_container_tools(
    mcp: MCPServer,
    containers: ContainerManager,
) -> None:
    """Register container management tools."""

    @mcp.tool()
    def docker_list_containers(all: bool = False) -> dict:
        """List Docker containers."""
        return _execute(containers.list_containers, all=all)

    @mcp.tool()
    def docker_get_container_info(container_id: str) -> dict:
        """Get detailed information about a Docker container."""
        return _execute(containers.get_container_info, container_id)

    @mcp.tool()
    def docker_run_container(
        image: str,
        name: str | None = None,
        command: str | None = None,
        ports: dict[str, Any] | None = None,
        environment: dict[str, str] | None = None,
        volumes_config: dict[str, Any] | None = None,
        detach: bool = True,
    ) -> dict:
        """Create and run a Docker container."""
        return _execute(
            containers.run_container,
            image=image,
            name=name,
            command=command,
            ports=ports,
            environment=environment,
            volumes=volumes_config,
            detach=detach,
        )

    @mcp.tool()
    def docker_start_container(container_id: str) -> dict:
        """Start a stopped Docker container."""
        return _execute(containers.start_container, container_id)

    @mcp.tool()
    def docker_stop_container(container_id: str, timeout: int = 10) -> dict:
        """Stop a running Docker container."""
        return _execute(containers.stop_container, container_id, timeout=timeout)

    @mcp.tool()
    def docker_restart_container(container_id: str, timeout: int = 10) -> dict:
        """Restart a Docker container."""
        return _execute(containers.restart_container, container_id, timeout=timeout)

    @mcp.tool()
    def docker_pause_container(container_id: str) -> dict:
        """Pause a running Docker container."""
        return _execute(containers.pause_container, container_id)

    @mcp.tool()
    def docker_unpause_container(container_id: str) -> dict:
        """Unpause a Docker container."""
        return _execute(containers.unpause_container, container_id)

    @mcp.tool()
    def docker_rename_container(container_id: str, new_name: str) -> dict:
        """Rename a Docker container."""
        return _execute(containers.rename_container, container_id, new_name)

    @mcp.tool()
    def docker_remove_container(
        container_id: str,
        force: bool = False,
        confirmed: bool = False,
    ) -> dict:
        """Remove a Docker container. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_remove_container")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(containers.remove_container, container_id, force=force)


# =========================================================
# Image Tools
# =========================================================

def _register_image_tools(
    mcp: MCPServer,
    images: ImageManager,
) -> None:
    """Register image management tools."""

    @mcp.tool()
    def docker_list_images() -> dict:
        """List Docker images."""
        return _execute(images.list_images)

    @mcp.tool()
    def docker_get_image_info(image_id: str) -> dict:
        """Get detailed information about a Docker image."""
        return _execute(images.get_image_info, image_id)

    @mcp.tool()
    def docker_pull_image(repository: str, tag: str = "latest") -> dict:
        """Pull a Docker image from a registry."""
        return _execute(images.pull_image, repository, tag=tag)

    @mcp.tool()
    def docker_push_image(repository: str, tag: str = "latest") -> dict:
        """Push a Docker image to a registry."""
        return _execute(images.push_image, repository, tag=tag)

    @mcp.tool()
    def docker_build_image(
        dockerfile_path: str,
        tag: str,
        buildargs: dict[str, str] | None = None,
    ) -> dict:
        """Build a Docker image from a Dockerfile."""
        return _execute(
            images.build_image,
            dockerfile_path=dockerfile_path,
            tag=tag,
            buildargs=buildargs,
        )

    @mcp.tool()
    def docker_tag_image(
        image_id: str,
        repository: str,
        tag: str = "latest",
    ) -> dict:
        """Tag a Docker image."""
        return _execute(images.tag_image, image_id, repository, tag=tag)

    @mcp.tool()
    def docker_search_image(term: str, limit: int = 10) -> dict:
        """Search Docker Hub for images."""
        return _execute(images.search_image, term, limit=limit)

    @mcp.tool()
    def docker_get_image_history(image_id: str, limit: int = 20) -> dict:
        """Get Docker image build history."""
        return _execute(images.get_image_history, image_id, limit=limit)

    @mcp.tool()
    def docker_remove_image(
        image_id: str,
        force: bool = False,
        confirmed: bool = False,
    ) -> dict:
        """Remove a Docker image. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_remove_image")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(images.remove_image, image_id, force=force)


# =========================================================
# Logs / Monitoring Tools
# =========================================================

def _register_logs_tools(
    mcp: MCPServer,
    logs: LogsManager,
) -> None:
    """Register logs and monitoring tools."""

    @mcp.tool()
    def docker_get_container_logs(container_id: str, tail: int = 50) -> dict:
        """Get recent Docker container logs."""
        return _execute(logs.get_container_logs, container_id, tail=tail)

    @mcp.tool()
    def docker_get_container_stats(container_id: str) -> dict:
        """Get container CPU, memory, network and I/O statistics."""
        return _execute(logs.get_container_stats, container_id)

    @mcp.tool()
    def docker_stream_container_logs(
        container_id: str,
        tail: int = 50,
        max_lines: int = 100,
    ) -> dict:
        """Read a bounded number of streamed Docker log lines."""
        return _execute(
            logs.stream_logs,
            container_id,
            tail=tail,
            max_lines=max_lines,
        )

    @mcp.tool()
    def docker_get_container_processes(container_id: str) -> dict:
        """Get processes running inside a Docker container."""
        return _execute(logs.get_container_processes, container_id)

    @mcp.tool()
    def docker_get_container_changes(container_id: str) -> dict:
        """Get filesystem changes inside a Docker container."""
        return _execute(logs.get_container_changes, container_id)


# =========================================================
# Network Tools
# =========================================================

def _register_network_tools(
    mcp: MCPServer,
    networks: NetworkManager,
) -> None:
    """Register network management tools."""

    @mcp.tool()
    def docker_list_networks() -> dict:
        """List Docker networks."""
        return _execute(networks.list_networks)

    @mcp.tool()
    def docker_get_network_info(network_id: str) -> dict:
        """Get detailed information about a Docker network."""
        return _execute(networks.get_network_info, network_id)

    @mcp.tool()
    def docker_create_network(
        name: str,
        driver: str = "bridge",
        options: dict[str, str] | None = None,
    ) -> dict:
        """Create a Docker network."""
        return _execute(
            networks.create_network,
            name=name,
            driver=driver,
            options=options,
        )

    @mcp.tool()
    def docker_connect_container_network(
        container_id: str,
        network_id: str,
        ipv4_address: str | None = None,
    ) -> dict:
        """Connect a Docker container to a network."""
        return _execute(
            networks.connect_container,
            container_id=container_id,
            network_id=network_id,
            ipv4_address=ipv4_address,
        )

    @mcp.tool()
    def docker_disconnect_container_network(
        container_id: str,
        network_id: str,
        force: bool = False,
    ) -> dict:
        """Disconnect a Docker container from a network."""
        return _execute(
            networks.disconnect_container,
            container_id=container_id,
            network_id=network_id,
            force=force,
        )

    @mcp.tool()
    def docker_remove_network(
        network_id: str,
        confirmed: bool = False,
    ) -> dict:
        """Remove a Docker network. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_remove_network")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(networks.remove_network, network_id)

    @mcp.tool()
    def docker_prune_networks(confirmed: bool = False) -> dict:
        """Remove unused Docker networks. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_prune_networks")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(networks.prune_networks)


# =========================================================
# Volume Tools
# =========================================================

def _register_volume_tools(
    mcp: MCPServer,
    volumes: VolumeManager,
) -> None:
    """Register volume management tools."""

    @mcp.tool()
    def docker_list_volumes() -> dict:
        """List Docker volumes."""
        return _execute(volumes.list_volumes)

    @mcp.tool()
    def docker_get_volume_info(volume_name: str) -> dict:
        """Get detailed information about a Docker volume."""
        return _execute(volumes.get_volume_info, volume_name)

    @mcp.tool()
    def docker_create_volume(
        name: str,
        driver: str = "local",
        labels: dict[str, str] | None = None,
        driver_opts: dict[str, str] | None = None,
    ) -> dict:
        """Create a Docker volume."""
        return _execute(
            volumes.create_volume,
            name=name,
            driver=driver,
            labels=labels,
            driver_opts=driver_opts,
        )

    @mcp.tool()
    def docker_remove_volume(
        volume_name: str,
        force: bool = False,
        confirmed: bool = False,
    ) -> dict:
        """Remove a Docker volume. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_remove_volume")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(volumes.remove_volume, volume_name, force=force)

    @mcp.tool()
    def docker_prune_volumes(confirmed: bool = False) -> dict:
        """Remove unused Docker volumes. Requires confirmation."""
        try:
            _require_confirmation(confirmed, "docker_prune_volumes")
        except DockerError as exc:
            return {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            }

        return _execute(volumes.prune_volumes)


# =========================================================
# Main Registration Function
# =========================================================

def register_docker_tools(
    mcp: MCPServer,
    context: AppContext,
    settings: Settings,
) -> None:
    """
    Register all Docker MCP tools.

    Signature changed to accept context and settings
    for scalability with other tools.
    """

    logger.info("Initializing Docker provider...")

    try:
        
        docker_provider = DockerClientProvider(
            retry_attempts=settings.docker_retry_attempts,
            retry_delay=settings.docker_retry_delay,
        )

        docker_client = docker_provider.get_client()

        context.register_provider("docker", docker_provider)

        logger.info("Docker client connected successfully")

    except Exception as exc:
        logger.error("Failed to initialize Docker provider: %s", exc)
        raise

    containers = ContainerManager(docker_client)
    images = ImageManager(docker_client)
    logs = LogsManager(docker_client)
    networks = NetworkManager(docker_client)
    volumes = VolumeManager(docker_client)

    logger.info("Registering container tools...")
    _register_container_tools(mcp, containers)

    logger.info("Registering image tools...")
    _register_image_tools(mcp, images)

    logger.info("Registering logs tools...")
    _register_logs_tools(mcp, logs)

    logger.info("Registering network tools...")
    _register_network_tools(mcp, networks)

    logger.info("Registering volume tools...")
    _register_volume_tools(mcp, volumes)

    logger.info("All Docker tools registered successfully")