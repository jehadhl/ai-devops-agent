class DockerError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "DOCKER_ERROR",
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code


class DockerConnectionError(DockerError):
    def __init__(
        self,
        message: str = "Unable to connect to Docker daemon",
    ) -> None:
        super().__init__(
            message=message,
            code="DOCKER_CONNECTION_ERROR",
        )


class DockerResourceNotFoundError(DockerError):
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
    ) -> None:

        self.resource_type = resource_type
        self.resource_id = resource_id

        super().__init__(
            message=(
                f"{resource_type} '{resource_id}' "
                "was not found"
            ),
            code="DOCKER_RESOURCE_NOT_FOUND",
        )


class DockerAPIError(DockerError):
    def __init__(
        self,
        operation: str,
        message: str,
    ) -> None:

        self.operation = operation

        super().__init__(
            message=f"Docker API error during {operation}: {message}",
            code="DOCKER_API_ERROR",
        )


class DockerValidationError(DockerError):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message=message,
            code="DOCKER_VALIDATION_ERROR",
        )


class DockerConflictError(DockerError):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message=message,
            code="DOCKER_CONFLICT",
        )