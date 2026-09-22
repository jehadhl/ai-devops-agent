# ai_devops_mcp/tools/docker/logs.py

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


class LogsManager:
    """Manage Docker container logs, statistics, and diagnostics."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client

    def get_container_logs(
        self,
        container_id: str,
        tail: int = 50,
    ) -> dict:
        """Get recent logs from a Docker container."""

        self._validate_container_id(container_id)
        self._validate_limit(tail, "tail")

        try:
            container = self._client.containers.get(container_id)

            logs = container.logs(
                tail=tail,
                timestamps=True,
                stream=False,
            )

            decoded_logs = logs.decode(
                "utf-8",
                errors="replace",
            )

            log_lines = [
                line
                for line in decoded_logs.splitlines()
                if line
            ]

            logger.info(
                "Retrieved %s log lines from container %s",
                len(log_lines),
                container_id,
            )

            return {
                "container_id": container.id,
                "container_name": container.name,
                "line_count": len(log_lines),
                "logs": log_lines,
                "timestamps": True,
            }

        except NotFound as exc:
            self._raise_not_found(exc, container_id)

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_container_logs",
            )

    def get_container_stats(
        self,
        container_id: str,
    ) -> dict:
        """Get container CPU, memory, network, I/O and PID statistics."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(container_id)

            stats = container.stats(stream=False)

            logger.info(
                "Retrieved stats for container %s",
                container_id,
            )

            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_usage = cpu_stats.get("cpu_usage", {})
            precpu_usage = precpu_stats.get("cpu_usage", {})

            cpu_total = cpu_usage.get("total_usage", 0)
            precpu_total = precpu_usage.get("total_usage", 0)

            system_total = cpu_stats.get(
                "system_cpu_usage",
                0,
            )
            presystem_total = precpu_stats.get(
                "system_cpu_usage",
                0,
            )

            cpu_delta = cpu_total - precpu_total
            system_delta = system_total - presystem_total

            online_cpus = cpu_stats.get("online_cpus")

            if not online_cpus:
                percpu_usage = cpu_usage.get(
                    "percpu_usage",
                    [],
                )
                online_cpus = len(percpu_usage) or 1

            if cpu_delta > 0 and system_delta > 0:
                cpu_percent = (
                    cpu_delta
                    / system_delta
                    * online_cpus
                    * 100.0
                )
            else:
                cpu_percent = 0.0

            memory_stats = stats.get(
                "memory_stats",
                {},
            )

            memory_usage_bytes = memory_stats.get(
                "usage",
                0,
            )

            memory_limit_bytes = memory_stats.get(
                "limit",
                0,
            )

            memory_usage_mb = (
                memory_usage_bytes / (1024**2)
            )

            memory_limit_mb = (
                memory_limit_bytes / (1024**2)
            )

            memory_percent = (
                memory_usage_bytes
                / memory_limit_bytes
                * 100.0
                if memory_limit_bytes > 0
                else 0.0
            )

            network_stats = self._parse_network_stats(
                stats.get("networks", {})
            )

            io_stats = self._parse_block_io(
                stats.get("blkio_stats", {})
            )

            pids = stats.get(
                "pids_stats",
                {},
            ).get("current", 0)

            return {
                "container_id": container.id,
                "container_name": container.name,
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "count": online_cpus,
                },
                "memory": {
                    "usage_mb": round(
                        memory_usage_mb,
                        2,
                    ),
                    "limit_mb": round(
                        memory_limit_mb,
                        2,
                    ),
                    "percent": round(
                        memory_percent,
                        2,
                    ),
                },
                "network": network_stats,
                "io": io_stats,
                "pids": pids,
            }

        except NotFound as exc:
            self._raise_not_found(exc, container_id)

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_container_stats",
            )

    def stream_logs(
        self,
        container_id: str,
        tail: int = 50,
        max_lines: int = 100,
    ) -> dict:
        """
        Read a limited number of streamed log lines.

        This method intentionally stops after max_lines
        to avoid an unbounded operation.
        """

        self._validate_container_id(container_id)
        self._validate_limit(tail, "tail")
        self._validate_limit(max_lines, "max_lines")

        try:
            container = self._client.containers.get(
                container_id
            )

            log_stream = container.logs(
                tail=tail,
                timestamps=True,
                stream=True,
                follow=True,
            )

            logger.info(
                "Started log stream for container %s",
                container_id,
            )

            log_lines: list[str] = []

            try:
                for line in log_stream:
                    decoded_line = line.decode(
                        "utf-8",
                        errors="replace",
                    ).strip()

                    if decoded_line:
                        log_lines.append(decoded_line)

                    if len(log_lines) >= max_lines:
                        break
            finally:
                close = getattr(
                    log_stream,
                    "close",
                    None,
                )

                if callable(close):
                    close()

            logger.info(
                "Collected %s streamed log lines from container %s",
                len(log_lines),
                container_id,
            )

            return {
                "container_id": container.id,
                "container_name": container.name,
                "streaming": True,
                "line_count": len(log_lines),
                "logs": log_lines,
            }

        except NotFound as exc:
            self._raise_not_found(exc, container_id)

        except APIError as exc:
            self._raise_api_error(
                exc,
                "stream_logs",
            )

    def get_container_processes(
        self,
        container_id: str,
    ) -> dict:
        """Get processes running inside a Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(
                container_id
            )

            processes = container.top()

            titles = processes.get("Titles", [])
            process_rows = processes.get(
                "Processes",
                [],
            )

            logger.info(
                "Retrieved %s processes from container %s",
                len(process_rows),
                container_id,
            )

            return {
                "container_id": container.id,
                "container_name": container.name,
                "titles": titles,
                "processes": process_rows,
                "process_count": len(process_rows),
            }

        except NotFound as exc:
            self._raise_not_found(exc, container_id)

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_container_processes",
            )

    def get_container_changes(
        self,
        container_id: str,
    ) -> dict:
        """Get filesystem changes made inside a Docker container."""

        self._validate_container_id(container_id)

        try:
            container = self._client.containers.get(
                container_id
            )

            changes = container.diff() or []

            logger.info(
                "Retrieved %s filesystem changes from container %s",
                len(changes),
                container_id,
            )

            added = [
                change
                for change in changes
                if change.get("Kind") == 1
            ]

            modified = [
                change
                for change in changes
                if change.get("Kind") == 0
            ]

            deleted = [
                change
                for change in changes
                if change.get("Kind") == 2
            ]

            return {
                "container_id": container.id,
                "container_name": container.name,
                "total_changes": len(changes),
                "added": len(added),
                "modified": len(modified),
                "deleted": len(deleted),
                "changes": changes,
            }

        except NotFound as exc:
            self._raise_not_found(exc, container_id)

        except APIError as exc:
            self._raise_api_error(
                exc,
                "get_container_changes",
            )

    @staticmethod
    def _parse_network_stats(
        networks: dict[str, Any],
    ) -> dict[str, dict[str, int]]:
        """Convert Docker network stats into a cleaner structure."""

        network_stats: dict[str, dict[str, int]] = {}

        for network_name, data in networks.items():
            network_stats[network_name] = {
                "rx_bytes": data.get("rx_bytes", 0),
                "tx_bytes": data.get("tx_bytes", 0),
                "rx_packets": data.get(
                    "rx_packets",
                    0,
                ),
                "tx_packets": data.get(
                    "tx_packets",
                    0,
                ),
            }

        return network_stats

    @staticmethod
    def _parse_block_io(
        blkio_stats: dict[str, Any],
    ) -> dict[str, int]:
        """Calculate Docker block I/O read/write bytes."""

        read_bytes = 0
        write_bytes = 0

        entries = blkio_stats.get(
            "io_service_bytes_recursive",
            [],
        ) or []

        for entry in entries:
            operation = str(
                entry.get("op", "")
            ).lower()

            value = entry.get("value", 0)

            if operation == "read":
                read_bytes += value

            elif operation == "write":
                write_bytes += value

        return {
            "read_bytes": read_bytes,
            "write_bytes": write_bytes,
        }

    @staticmethod
    def _validate_container_id(
        container_id: str,
    ) -> None:
        """Validate container ID or name."""

        if not container_id or not container_id.strip():
            raise DockerValidationError(
                "Container ID or name must not be empty."
            )

    @staticmethod
    def _validate_limit(
        value: int,
        field_name: str,
    ) -> None:
        """Validate bounded log/query limits."""

        if value < 1 or value > 10_000:
            raise DockerValidationError(
                f"{field_name} must be between 1 and 10000."
            )

    @staticmethod
    def _raise_not_found(
        exc: NotFound,
        container_id: str,
    ) -> None:
        """Translate Docker SDK NotFound exception."""

        raise DockerResourceNotFoundError(
            resource_type="Container",
            resource_id=container_id,
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