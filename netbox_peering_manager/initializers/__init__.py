# ruff: noqa: F401
# Import all initializers to register them with netbox-initializers
import contextlib

with contextlib.suppress(ImportError, Exception):
    from .relationships import RelationshipInitializer
