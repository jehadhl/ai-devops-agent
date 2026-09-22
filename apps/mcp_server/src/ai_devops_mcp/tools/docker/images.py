import logging
from pathlib import Path
from typing import Any

from docker import DockerClient
from docker.errors import APIError, BuildError, ImageNotFound, NotFound

from .exceptions import (
    DockerAPIError,
    DockerResourceNotFoundError,
    DockerValidationError,
)


logger = logging.getLogger(__name__)


class ImageManager:
    """Manage Docker image operations."""
    """depennecy injection of docker client to avoid multiple connections to docker daemon"""
    def __init__(self, client: DockerClient) -> None:
        self._client = client

    def list_images(self) -> dict:
        """List Docker images."""
        try:
            images = self._client.images.list()

            logger.info("Listed %s Docker images", len(images))

            return {
                "count": len(images),
                "images": [
                    {
                        "id": image.id[:12],
                        "tags": image.tags,
                        "size_mb": round(
                            image.attrs.get("Size", 0) / (1024 * 1024),
                            2,
                        ),
                        "created": image.attrs.get("Created"),
                        "architecture": image.attrs.get(
                            "Architecture",
                            "unknown",
                        ),
                    }
                    for image in images
                ],
            }

        except APIError as exc:
            self._raise_api_error(exc, "list_images")

    def get_image_info(self, image_id: str) -> dict:
        """Get detailed information about a Docker image."""

        self._validate_image_id(image_id)

        try:
            image = self._client.images.get(image_id)

            logger.info(
                "Retrieved information for Docker image %s",
                image_id,
            )

            config = image.attrs.get("Config", {})

            # Do not expose environment variable values to MCP/AI.
            env_keys = [
                item.split("=", 1)[0]
                for item in config.get("Env", []) or []
            ]

            return {
                "id": image.id,
                "tags": image.tags,
                "size_mb": round(
                    image.attrs.get("Size", 0) / (1024 * 1024),
                    2,
                ),
                "created": image.attrs.get("Created"),
                "os": image.attrs.get("Os", "unknown"),
                "architecture": image.attrs.get(
                    "Architecture",
                    "unknown",
                ),
                "config": {
                    "cmd": config.get("Cmd"),
                    "env_keys": env_keys,
                    "entrypoint": config.get("Entrypoint"),
                },
            }

        except ImageNotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Image",
                resource_id=image_id,
            )

        except APIError as exc:
            self._raise_api_error(exc, "get_image_info")

    def pull_image(
        self,
        repository: str,
        tag: str = "latest",
    ) -> dict:
        """Pull an image from a Docker registry."""

        self._validate_repository(repository)
        self._validate_tag(tag)

        image_name = f"{repository}:{tag}"

        try:
            logger.info(
                "Pulling Docker image %s",
                image_name,
            )

            image = self._client.images.pull(
                repository,
                tag=tag,
            )

            logger.info(
                "Pulled Docker image %s",
                image_name,
            )

            return {
                "id": image.id,
                "repository": repository,
                "tag": tag,
                "image": image_name,
                "status": "pulled",
            }

        except ImageNotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Image",
                resource_id=image_name,
            )

        except APIError as exc:
            self._raise_api_error(exc, "pull_image")

    def push_image(
        self,
        repository: str,
        tag: str = "latest",
    ) -> dict:
        """Push an image to a Docker registry."""

        self._validate_repository(repository)
        self._validate_tag(tag)

        image_name = f"{repository}:{tag}"

        try:
            logger.info(
                "Pushing Docker image %s",
                image_name,
            )

            response = self._client.images.push(
                repository,
                tag=tag,
            )

            logger.info(
                "Pushed Docker image %s",
                image_name,
            )

            return {
                "repository": repository,
                "tag": tag,
                "image": image_name,
                "status": "pushed",
                "response": response,
            }

        except APIError as exc:
            self._raise_api_error(exc, "push_image")

    def build_image(
        self,
        dockerfile_path: str,
        tag: str,
        buildargs: dict[str, str] | None = None,
    ) -> dict:
        """Build a Docker image from a Dockerfile."""

        self._validate_tag(tag)

        if not dockerfile_path or not dockerfile_path.strip():
            raise DockerValidationError(
                "Dockerfile path must not be empty."
            )

        path = Path(dockerfile_path)

        if not path.is_file():
            raise DockerValidationError(
                f"Dockerfile not found: {dockerfile_path}"
            )

        try:
            logger.info(
                "Building Docker image from %s with tag %s",
                dockerfile_path,
                tag,
            )

            with path.open("rb") as dockerfile:
                image, build_logs = self._client.images.build(
                    fileobj=dockerfile,
                    tag=tag,
                    buildargs=buildargs,
                    rm=True,
                )

            # Docker SDK returns an iterator for build logs.
            logs = list(build_logs)

            logger.info(
                "Built Docker image %s",
                tag,
            )

            return {
                "id": image.id[:12],
                "tag": tag,
                "status": "built",
                "logs": logs[-5:],
            }

        except BuildError as exc:
            raise DockerAPIError(
                operation="build_image",
                message=str(exc),
            ) from exc

        except APIError as exc:
            self._raise_api_error(exc, "build_image")

    def tag_image(
        self,
        image_id: str,
        repository: str,
        tag: str = "latest",
    ) -> dict:
        """Tag a Docker image."""

        self._validate_image_id(image_id)
        self._validate_repository(repository)
        self._validate_tag(tag)

        try:
            image = self._client.images.get(image_id)

            success = image.tag(
                repository,
                tag=tag,
            )

            if not success:
                raise DockerAPIError(
                    operation="tag_image",
                    message=(
                        f"Failed to tag image '{image_id}' "
                        f"as '{repository}:{tag}'"
                    ),
                )

            image_name = f"{repository}:{tag}"

            logger.info(
                "Tagged Docker image %s as %s",
                image_id,
                image_name,
            )

            return {
                "id": image.id,
                "repository": repository,
                "tag": tag,
                "image": image_name,
                "status": "tagged",
            }

        except ImageNotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Image",
                resource_id=image_id,
            )

        except APIError as exc:
            self._raise_api_error(exc, "tag_image")

    def remove_image(
        self,
        image_id: str,
        force: bool = False,
        noprune: bool = False,
    ) -> dict:
        """Remove a Docker image."""

        self._validate_image_id(image_id)

        try:
            self._client.images.remove(
                image=image_id,
                force=force,
                noprune=noprune,
            )

            logger.info(
                "Removed Docker image %s",
                image_id,
            )

            return {
                "id": image_id,
                "status": "removed",
            }

        except ImageNotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Image",
                resource_id=image_id,
            )

        except APIError as exc:
            self._raise_api_error(exc, "remove_image")

    def search_image(
        self,
        term: str,
        limit: int = 10,
    ) -> dict:
        """Search for images on Docker Hub."""

        if not term or not term.strip():
            raise DockerValidationError(
                "Search term must not be empty."
            )

        if limit < 1 or limit > 100:
            raise DockerValidationError(
                "Search limit must be between 1 and 100."
            )

        try:
            results = self._client.images.search(term)

            logger.info(
                "Searched Docker images for %s",
                term,
            )

            selected_results = results[:limit]

            return {
                "search_term": term,
                "count": len(selected_results),
                "results": [
                    {
                        "name": result.get("name"),
                        "description": result.get("description"),
                        "stars": result.get("star_count"),
                        "official": result.get("is_official"),
                        "automated": result.get("is_automated"),
                    }
                    for result in selected_results
                ],
            }

        except APIError as exc:
            self._raise_api_error(exc, "search_image")

    def get_image_history(
        self,
        image_id: str,
        limit: int = 20,
    ) -> dict:
        """Get Docker image build history."""

        self._validate_image_id(image_id)

        if limit < 1 or limit > 100:
            raise DockerValidationError(
                "History limit must be between 1 and 100."
            )

        try:
            image = self._client.images.get(image_id)
            history = image.history()

            logger.info(
                "Retrieved history for Docker image %s",
                image_id,
            )

            selected_history = history[:limit]

            return {
                "image_id": image_id,
                "history_count": len(selected_history),
                "history": selected_history,
            }

        except ImageNotFound as exc:
            self._raise_not_found(
                exc,
                resource_type="Image",
                resource_id=image_id,
            )

        except APIError as exc:
            self._raise_api_error(exc, "get_image_history")

    @staticmethod
    def _validate_image_id(image_id: str) -> None:
        """Validate an image ID or name."""

        if not image_id or not image_id.strip():
            raise DockerValidationError(
                "Image ID or name must not be empty."
            )

    @staticmethod
    def _validate_repository(repository: str) -> None:
        """Validate a Docker repository name."""

        if not repository or not repository.strip():
            raise DockerValidationError(
                "Repository must not be empty."
            )

    @staticmethod
    def _validate_tag(tag: str) -> None:
        """Validate a Docker image tag."""

        if not tag or not tag.strip():
            raise DockerValidationError(
                "Image tag must not be empty."
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