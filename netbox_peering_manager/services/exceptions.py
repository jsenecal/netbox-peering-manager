"""Exceptions for PeeringDB integration."""


class PeeringDBError(Exception):
    """Base exception for PeeringDB operations."""


class PeeringDBAPIError(PeeringDBError):
    """API request failed."""


class PeeringDBNotFoundError(PeeringDBError):
    """IX/Network not found in PeeringDB."""
