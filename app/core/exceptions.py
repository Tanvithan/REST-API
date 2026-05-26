class ServiceError(Exception):
    status_code = 500
    detail = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class DuplicateResourceError(ServiceError):
    status_code = 409
    detail = "Resource already exists."


class ResourceNotFoundError(ServiceError):
    status_code = 404
    detail = "Resource not found."


class ExternalAPIError(ServiceError):
    status_code = 502
    detail = "External API returned an error."


class ExternalServiceUnavailableError(ServiceError):
    status_code = 503
    detail = "External service unavailable."