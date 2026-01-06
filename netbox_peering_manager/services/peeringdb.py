"""PeeringDB API client."""

import logging

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from netbox_peering_manager.constants import (
    PEERINGDB_DEFAULT_TIMEOUT,
    PEERINGDB_DEFAULT_URL,
)
from netbox_peering_manager.services.exceptions import (
    PeeringDBAPIError,
    PeeringDBNotFoundError,
)

logger = logging.getLogger(__name__)


def get_plugin_config(key: str, default=None):
    """Get plugin configuration value."""
    from django.conf import settings

    plugin_settings = settings.PLUGINS_CONFIG.get("netbox_peering_manager", {})
    return plugin_settings.get(key, default)


class PeeringDBClient:
    """Client for PeeringDB REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        self.base_url = base_url or get_plugin_config("peeringdb_url") or PEERINGDB_DEFAULT_URL
        self.api_key = api_key or get_plugin_config("peeringdb_api_key")
        self.timeout = timeout or get_plugin_config("peeringdb_timeout") or PEERINGDB_DEFAULT_TIMEOUT
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Api-Key {self.api_key}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True,
    )
    def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make API request with retry logic."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.debug(f"PeeringDB request: {url}")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                msg = f"Not found: {endpoint}"
                raise PeeringDBNotFoundError(msg) from e
            msg = f"API error: {e}"
            raise PeeringDBAPIError(msg, status_code=e.response.status_code) from e
        except requests.RequestException as e:
            logger.warning(f"PeeringDB request failed, retrying: {e}")
            raise

    def get_ix(self, ix_id: int) -> dict:
        """Fetch IX details by PeeringDB ID."""
        data = self._request(f"ix/{ix_id}")
        if not data.get("data"):
            msg = f"IX {ix_id} not found"
            raise PeeringDBNotFoundError(msg)
        return data["data"][0]

    def get_ixlans(self, ix_id: int) -> list[dict]:
        """Fetch all IXLANs for an IX."""
        data = self._request("ixlan", params={"ix_id": ix_id})
        return data.get("data", [])

    def get_ixlan_prefixes(self, ixlan_id: int) -> list[dict]:
        """Fetch prefixes for an IXLAN."""
        data = self._request("ixpfx", params={"ixlan_id": ixlan_id})
        return data.get("data", [])

    def get_netixlans(self, ixlan_id: int) -> list[dict]:
        """Fetch all network connections on an IXLAN (peers)."""
        data = self._request("netixlan", params={"ixlan_id": ixlan_id})
        return data.get("data", [])

    def get_network(self, asn: int) -> dict:
        """Fetch network details by ASN."""
        data = self._request("net", params={"asn": asn})
        if not data.get("data"):
            msg = f"Network AS{asn} not found"
            raise PeeringDBNotFoundError(msg)
        return data["data"][0]

    def search_ix(self, query: str) -> list[dict]:
        """Search IXes by name."""
        data = self._request("ix", params={"name__contains": query})
        return data.get("data", [])
