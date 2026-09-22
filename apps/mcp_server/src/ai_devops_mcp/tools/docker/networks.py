# ai_devops_mcp/tools/docker/networks.py

import logging
from typing import Any

from docker import DockerClient
from docker.errors import APIError, NotFound

from .exceptions import (
    DockerAPIError,
    DockerResourceNotFoundError,
    DockerValidationError,
)


logger = logging.getLogger(__name__)


class NetworkManager:
    """Manage Docker network operations."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client

    def list_networks(self) -> dict:
        """List all Docker networks."""

        try:
            networks = self._client.networks.list()

            logger.info(
                "Listed %s Docker networks",
                len(networks),
            )

            return {
                "count": len(networks),
                "networks": [
                    {
                        "id": network.id[:12],
                        "name": network.name,
                        "driver": network.attrs.get("Driver"),
                        "scope": network.attrs.get("Scope"),
                        "container_count": len(
                            network.attrs.get("Containers", {}) or {}
                        ),
                        "ipam": network.attrs.get("IPAM", {}),
                    }
                    for network in networks
                ],
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "list_networks",
            )

    def get_network_info(
        self,
        network_id: str,
    ) -> dict:
        """Get detailed information about a Docker network."""

        self._validate_network_id(network_id)

        try:
            network = self._client.networks.get(network_id)

            logger.info(
                "Retrieved information for Docker network %s",
                network_id,
            )

            return {
                "id": network.id,
                "name": network.name,
                "driver": network.attrs.get("Driver"),
                "scope": network.attrs.get("Scope"),
                "containers": network.attrs.get(
                    "Containers",
                    {},
                ),
                "ipam": network.attrs.get(
                    "IPAM",
                    {},
                ),
                "options": network.attrs.get(
                    "Options",
                    {},
                ),
                "labels": network.attrs.get(
                    "Labels",
                    {},
                ),
            }

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Network",
                resource_id=network_id,
            )

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_network_info",
            )

    def create_network(
        self,
        name: str,
        driver: str = "bridge",
        options: dict[str, str] | None = None,
    ) -> dict:
        """Create a Docker network."""

        self._validate_network_name(name)
        self._validate_driver(driver)

        try:
            network = self._client.networks.create(
                name=name,
                driver=driver,
                options=options,
            )

            logger.info(
                "Created Docker network %s",
                name,
            )

            return {
                "id": network.id,
                "name": network.name,
                "driver": driver,
                "status": "created",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "create_network",
            )

    def remove_network(
        self,
        network_id: str,
    ) -> dict:
        """Remove a Docker network."""

        self._validate_network_id(network_id)

        try:
            network = self._client.networks.get(
                network_id
            )

            # Save values before removing the network.
            network_id_full = network.id
            network_name = network.name

            network.remove()

            logger.info(
                "Removed Docker network %s",
                network_id,
            )

            return {
                "id": network_id_full,
                "name": network_name,
                "status": "removed",
            }

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Network",
                resource_id=network_id,
            )

        except APIError as exc:
            self._raise_api_error(
                exc,
                "remove_network",
            )

    def connect_container(
        self,
        container_id: str,
        network_id: str,
        ipv4_address: str | None = None,
    ) -> dict:
        """Connect a Docker container to a network."""

        self._validate_container_id(container_id)
        self._validate_network_id(network_id)

        try:
            network = self._client.networks.get(
                network_id
            )

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Network",
                resource_id=network_id,
            )

        try:
            container = self._client.containers.get(
                container_id
            )

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Container",
                resource_id=container_id,
            )

        try:
            network.connect(
                container,
                ipv4_address=ipv4_address,
            )

            logger.info(
                "Connected container %s to network %s",
                container_id,
                network_id,
            )

            return {
                "container_id": container.id,
                "container_name": container.name,
                "network_id": network.id,
                "network_name": network.name,
                "ipv4_address": ipv4_address,
                "status": "connected",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "connect_container",
            )

    def disconnect_container(
        self,
        container_id: str,
        network_id: str,
        force: bool = False,
    ) -> dict:
        """Disconnect a Docker container from a network."""

        self._validate_container_id(container_id)
        self._validate_network_id(network_id)

        try:
            network = self._client.networks.get(
                network_id
            )

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Network",
                resource_id=network_id,
            )

        try:
            container = self._client.containers.get(
                container_id
            )

        except NotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Container",
                resource_id=container_id,
            )

        try:
            network.disconnect(
                container,
                force=force,
            )

            logger.info(
                "Disconnected container %s from network %s",
                container_id,
                network_id,
            )

            return {
                "container_id": container.id,
                "container_name": container.name,
                "network_id": network.id,
                "network_name": network.name,
                "status": "disconnected",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "disconnect_container",
            )

    def prune_networks(self) -> dict:
        """
        Remove unused Docker networks.

        Warning:
        This is a destructive operation.
        """

        try:
            result = self._client.networks.prune()

            deleted_networks = (
                result.get("NetworksDeleted", []) or []
            )

            logger.info(
                "Pruned %s Docker networks",
                len(deleted_networks),
            )

            return {
                "deleted_count": len(deleted_networks),
                "networks_deleted": deleted_networks,
                "status": "pruned",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "prune_networks",
            )

    @staticmethod
    def _validate_network_id(
        network_id: str,
    ) -> None:
        """Validate Docker network ID or name."""

        if not network_id or not network_id.strip():
            raise DockerValidationError(
                "Network ID or name must not be empty."
            )

    @staticmethod
    def _validate_network_name(
        name: str,
    ) -> None:
        """Validate Docker network name."""

        if not name or not name.strip():
            raise DockerValidationError(
                "Network name must not be empty."
            )

    @staticmethod
    def _validate_container_id(
        container_id: str,
    ) -> None:
        """Validate Docker container ID or name."""

        if not container_id or not container_id.strip():
            raise DockerValidationError(
                "Container ID or name must not be empty."
            )

    @staticmethod
    def _validate_driver(
        driver: str,
    ) -> None:
        """Validate Docker network driver."""

        if not driver or not driver.strip():
            raise DockerValidationError(
                "Network driver must not be empty."
            )

    @staticmethod
    def _raise_not_found(
        exc: NotFound,
        resource_type: str,
        resource_id: str,
    ) -> None:
        """Translate Docker SDK NotFound exception."""

        raise DockerResourceNotFoundError(
            resource_type=resource_type,
            resource_id=resource_id,
        ) from exc

    @staticmethod
    def _raise_api_error(
        exc: APIError,
        operation: str,
    ) -> None:
        """Translate Docker SDK APIError exception."""

        raise DockerAPIError(
            operation=operation,
            message=str(exc),
        ) from exc