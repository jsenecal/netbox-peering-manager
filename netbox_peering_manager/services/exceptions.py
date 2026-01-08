"""Exceptions for PeeringDB integration."""


class PeeringDBError(Exception):
    """Base exception for PeeringDB operations."""


class PeeringDBAPIError(PeeringDBError):
    """API request failed."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class PeeringDBNotFoundError(PeeringDBError):
    """IX/Network not found in PeeringDB."""


class PeeringDBRateLimitError(PeeringDBError):
    """Rate limit exceeded (429 response)."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")
