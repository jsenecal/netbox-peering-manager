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
