# ai_devops_mcp/tools/docker/volumes.py

import logging

from docker import DockerClient
from docker.errors import APIError, NotFound

from .exceptions import (
    DockerAPIError,
    DockerResourceNotFoundError,
    DockerValidationError,
)


logger = logging.getLogger(__name__)


class VolumeManager:
    """Manage Docker volume operations."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client

    def list_volumes(self) -> dict:
        """List all Docker volumes."""

        try:
            volumes = self._client.volumes.list()

            logger.info(
                "Listed %s Docker volumes",
                len(volumes),
            )

            return {
                "count": len(volumes),
                "volumes": [
                    {
                        "name": volume.name,
                        "driver": volume.attrs.get("Driver"),
                        "mountpoint": volume.attrs.get("Mountpoint"),
                        "labels": volume.attrs.get("Labels", {}) or {},
                        "options": volume.attrs.get("Options", {}) or {},
                        "scope": volume.attrs.get("Scope"),
                        "created": volume.attrs.get("CreatedAt"),
                    }
                    for volume in volumes
                ],
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "list_volumes",
            )

    def get_volume_info(
        self,
        volume_name: str,
    ) -> dict:
        """Get detailed information about a Docker volume."""

        self._validate_volume_name(volume_name)

        try:
            volume = self._client.volumes.get(volume_name)

            logger.info(
                "Retrieved information for Docker volume %s",
                volume_name,
            )

            usage_data = volume.attrs.get(
                "UsageData",
                {},
            ) or {}

            size_bytes = usage_data.get("Size")

            size_mb = (
                round(size_bytes / (1024**2), 2)
                if isinstance(size_bytes, int) and size_bytes >= 0
                else None
            )

            return {
                "name": volume.name,
                "driver": volume.attrs.get("Driver"),
                "mountpoint": volume.attrs.get("Mountpoint"),
                "labels": volume.attrs.get("Labels", {}) or {},
                "options": volume.attrs.get("Options", {}) or {},
                "scope": volume.attrs.get("Scope"),
                "created": volume.attrs.get("CreatedAt"),
                "usage": {
                    "ref_count": usage_data.get("RefCount"),
                    "size_bytes": size_bytes,
                    "size_mb": size_mb,
                },
            }

        except NotFound as exc:
            self._raise_not_found(
                exc,
                volume_name,
            )

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_volume_info",
            )

    def create_volume(
        self,
        name: str,
        driver: str = "local",
        labels: dict[str, str] | None = None,
        driver_opts: dict[str, str] | None = None,
    ) -> dict:
        """Create a new Docker volume."""

        self._validate_volume_name(name)
        self._validate_driver(driver)

        try:
            volume = self._client.volumes.create(
                name=name,
                driver=driver,
                labels=labels,
                driver_opts=driver_opts,
            )

            logger.info(
                "Created Docker volume %s",
                name,
            )

            return {
                "name": volume.name,
                "driver": volume.attrs.get(
                    "Driver",
                    driver,
                ),
                "mountpoint": volume.attrs.get(
                    "Mountpoint"
                ),
                "status": "created",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "create_volume",
            )

    def remove_volume(
        self,
        volume_name: str,
        force: bool = False,
    ) -> dict:
        """Remove a Docker volume."""

        self._validate_volume_name(volume_name)

        try:
            volume = self._client.volumes.get(
                volume_name
            )

            # Save information before removal.
            name = volume.name
            driver = volume.attrs.get("Driver")

            volume.remove(force=force)

            logger.info(
                "Removed Docker volume %s",
                volume_name,
            )

            return {
                "name": name,
                "driver": driver,
                "status": "removed",
            }

        except NotFound as exc:
            self._raise_not_found(
                exc,
                volume_name,
            )

        except APIError as exc:
            self._raise_api_error(
                exc,
                "remove_volume",
            )

    def prune_volumes(self) -> dict:
        """
        Remove unused Docker volumes.

        Warning:
        This is a destructive operation.
        """

        try:
            result = self._client.volumes.prune()

            deleted_volumes = (
                result.get("VolumesDeleted", []) or []
            )

            space_reclaimed_bytes = result.get(
                "SpaceReclaimed",
                0,
            ) or 0

            space_reclaimed_mb = round(
                space_reclaimed_bytes / (1024**2),
                2,
            )

            logger.info(
                "Pruned %s Docker volumes and reclaimed %.2f MB",
                len(deleted_volumes),
                space_reclaimed_mb,
            )

            return {
                "deleted_count": len(deleted_volumes),
                "volumes_deleted": deleted_volumes,
                "space_reclaimed_bytes": space_reclaimed_bytes,
                "space_reclaimed_mb": space_reclaimed_mb,
                "status": "pruned",
            }

        except APIError as exc:
            self._raise_api_error(
                exc,
                "prune_volumes",
            )

    @staticmethod
    def _validate_volume_name(
        volume_name: str,
    ) -> None:
        """Validate Docker volume name."""

        if not volume_name or not volume_name.strip():
            raise DockerValidationError(
                "Volume name must not be empty."
            )

    @staticmethod
    def _validate_driver(
        driver: str,
    ) -> None:
        """Validate Docker volume driver."""

        if not driver or not driver.strip():
            raise DockerValidationError(
                "Volume driver must not be empty."
            )

    @staticmethod
    def _raise_not_found(
        exc: NotFound,
        volume_name: str,
    ) -> None:
        """Translate Docker SDK NotFound exception."""

        raise DockerResourceNotFoundError(
            resource_type="Volume",
            resource_id=volume_name,
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