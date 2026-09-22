# ai_devops_mcp/tools/docker/containers.py

import logging
from typing import Any

from docker import DockerClient
from docker.errors import APIError, DockerException, ImageNotFound, NotFound

from .exceptions import (
    DockerAPIError,
    DockerError,
    DockerResourceNotFoundError,
    DockerValidationError,
)


logger = logging.getLogger(__name__)


class ContainerManager:
    """Manage Docker container operations."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client

    def list_containers(
        self,
        all: bool = False,
        filters: dict[str, Any] | None = None,
    ) -> dict:
        """List Docker containers."""
        try:
            containers = self._client.containers.list(
                all=all,
                filters=filters,
            )

            logger.info("Listed %s Docker containers", len(containers))

            return {
                "count": len(containers),
                "containers": [
                    {
                        "id": container.id[:12],
                        "name": container.name,
                        "status": container.status,
                        "image": (
                            container.image.tags[0]
                            if container.image.tags
                            else container.image.id[:12]
                        ),
                        "ports": container.ports,
                        "created": container.attrs.get("Created"),
                    }
                    for container in containers
                ],
            }

        except APIError as exc:
            self._raise_api_error(exc, "list_containers")

    def get_container_info(self, container_id: str) -> dict:
        """Get detailed information about a Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            logger.info(
                "Retrieved information for container %s",
                container_id,
            )

            config = container.attrs.get("Config", {})
            state = container.attrs.get("State", {})

            # Do NOT expose environment variable values to the MCP/AI.
            env_keys = [
                item.split("=", 1)[0]
                for item in config.get("Env", []) or []
            ]

            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags,
                "ports": container.ports,
                "mounts": container.attrs.get("Mounts", []),
                "env_keys": env_keys,
                "created": container.attrs.get("Created"),
                "started": state.get("StartedAt"),
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "get_container_info")

    def run_container(
        self,
        image: str,
        name: str | None = None,
        command: str | list[str] | None = None,
        ports: dict[str, Any] | None = None,
        environment: dict[str, str] | None = None,
        volumes: dict[str, Any] | None = None,
        detach: bool = True,
    ) -> dict:
        """Create and run a Docker container."""

        if not image or not image.strip():
            raise DockerValidationError(
                "Image name must not be empty."
            )

        try:
            container = self._client.containers.run(
                image=image,
                name=name,
                command=command,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=detach,
            )

            logger.info(
                "Started Docker container %s",
                container.id[:12],
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
            }

        except ImageNotFound as exc:
            self._raise_not_found(exc, "Image", image)

        except APIError as exc:
            self._raise_api_error(exc, "run_container")

    def stop_container(
        self,
        container_id: str,
        timeout: int = 10,
    ) -> dict:
        """Stop a running Docker container."""

        self._validate_container_id(container_id)

        if timeout < 0:
            raise DockerValidationError(
                "Timeout must be greater than or equal to 0."
            )

        try:
            container = self._client.containers.get(container_id)

            container.stop(timeout=timeout)

            logger.info(
                "Stopped Docker container %s",
                container_id,
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": "stopped",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "stop_container")

    def start_container(self, container_id: str) -> dict:
        """Start a stopped Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            container.start()

            logger.info(
                "Started Docker container %s",
                container_id,
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "start_container")

    def restart_container(
        self,
        container_id: str,
        timeout: int = 10,
    ) -> dict:
        """Restart a Docker container."""

        self._validate_container_id(container_id)

        if timeout < 0:
            raise DockerValidationError(
                "Timeout must be greater than or equal to 0."
            )

        try:
            container = self._client.containers.get(container_id)

            container.restart(timeout=timeout)

            logger.info(
                "Restarted Docker container %s",
                container_id,
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "restart_container")

    def remove_container(
        self,
        container_id: str,
        force: bool = False,
    ) -> dict:
        """Remove a Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            # Save values before removal.
            container_id_full = container.id
            container_name = container.name

            container.remove(force=force)

            logger.info(
                "Removed Docker container %s",
                container_id,
            )

            return {
                "id": container_id_full,
                "name": container_name,
                "status": "removed",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "remove_container")

    def pause_container(self, container_id: str) -> dict:
        """Pause a running Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            container.pause()

            logger.info(
                "Paused Docker container %s",
                container_id,
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": "paused",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "pause_container")

    def unpause_container(self, container_id: str) -> dict:
        """Unpause a Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            container.unpause()

            logger.info(
                "Unpaused Docker container %s",
                container_id,
            )

            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "unpause_container")

    def rename_container(
        self,
        container_id: str,
        new_name: str,
    ) -> dict:
        """Rename a Docker container."""

        self._validate_container_id(container_id)

        if not new_name or not new_name.strip():
            raise DockerValidationError(
                "New container name must not be empty."
            )

        try:
            container = self._client.containers.get(container_id)

            # Important: save the old name BEFORE rename().
            old_name = container.name

            container.rename(new_name)

            logger.info(
                "Renamed Docker container %s from %s to %s",
                container_id,
                old_name,
                new_name,
            )

            return {
                "id": container.id,
                "old_name": old_name,
                "new_name": new_name,
                "status": "renamed",
            }

        except NotFound as exc:
            self._raise_not_found(exc, "Container", container_id)

        except APIError as exc:
            self._raise_api_error(exc, "rename_container")


    @staticmethod
    def _validate_container_id(container_id: str) -> None:
        """Validate a container ID or name."""

        if not container_id or not container_id.strip():
            raise DockerValidationError(
                "Container ID or name must not be empty."
            )

    @staticmethod
    def _raise_not_found(
        exc: NotFound,
        resource_type: str,
        resource_id: str,
    ) -> None:
        """Translate Docker SDK NotFound into application exception."""

        raise DockerResourceNotFoundError(
            resource_type=resource_type,
            resource_id=resource_id,
        ) from exc

    @staticmethod
    def _raise_api_error(
        exc: APIError,
        operation: str,
    ) -> None:
        """Translate Docker SDK APIError into application exception."""

        raise DockerAPIError(
            operation=operation,
            message=str(exc),
        ) from exc