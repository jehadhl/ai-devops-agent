import logging
import time

import docker
from docker import DockerClient
from docker.errors import DockerException


logger = logging.getLogger(__name__)


class DockerClientProvider:
    """
    Creates and manages a shared Docker SDK client.
    Responsibilities:
    - Connect to the Docker daemon
    - Verify the connection
    - Retry failed connections
    - Provide the shared Docker client
    - Check connection health
    - Close the client
    """

    def __init__(
        self,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self._client: DockerClient | None = None
        self._retry_attempts = retry_attempts
        self._retry_delay = retry_delay

    def get_client(self) -> DockerClient:
        """
        Return the existing Docker client or create a new one.
        """

        if self._client is None:
            self._client = self._connect()

        return self._client

    def _connect(self) -> DockerClient:
        """
        Connect to Docker daemon with retry and exponential backoff.
        """

        last_error: DockerException | None = None

        for attempt in range(1, self._retry_attempts + 1):
            try:
                logger.info(
                    "Connecting to Docker daemon (attempt %s/%s)",
                    attempt,
                    self._retry_attempts,
                )

                client = docker.from_env()

                # Verify Docker daemon is reachable
                client.ping()

                logger.info("Successfully connected to Docker daemon")

                return client

            except DockerException as exc:
                last_error = exc

                logger.warning(
                    "Docker connection attempt %s/%s failed: %s",
                    attempt,
                    self._retry_attempts,
                    exc,
                )

                if attempt < self._retry_attempts:
                    delay = self._retry_delay * (2 ** (attempt - 1))

                    logger.debug(
                        "Retrying Docker connection in %.1f seconds",
                        delay,
                    )

                    time.sleep(delay)

        raise RuntimeError(
            f"Unable to connect to Docker daemon after "
            f"{self._retry_attempts} attempts"
        ) from last_error

    def is_connected(self) -> bool:
        """
        Check whether the Docker daemon is reachable.
        """

        if self._client is None:
            return False

        try:
            self._client.ping()
            return True

        except DockerException:
            return False

    def reconnect(self) -> DockerClient:
        """
        Close the current client and establish a new connection.
        """

        self.close()

        logger.info("Reconnecting to Docker daemon")

        self._client = self._connect()

        return self._client

    def close(self) -> None:
        """
        Close the Docker client.
        """

        if self._client is None:
            return

        try:
            self._client.close()
            logger.info("Docker client connection closed")

        except Exception:
            logger.exception("Error while closing Docker client")

        finally:
            self._client = None