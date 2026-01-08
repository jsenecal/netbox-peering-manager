# netbox_peering_manager/constants.py
"""Constants for netbox_peering_manager plugin."""

PEERINGDB_DEFAULT_URL = "https://www.peeringdb.com/api"
PEERINGDB_DEFAULT_TIMEOUT = 30
PEERINGDB_DEFAULT_RATE_LIMIT = 2.0  # Minimum seconds between requests (PeeringDB recommends >= 2s)
