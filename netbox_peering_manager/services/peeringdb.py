"""PeeringDB API client."""

import logging
import time

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from netbox_peering_manager.constants import (
    PEERINGDB_DEFAULT_RATE_LIMIT,
    PEERINGDB_DEFAULT_TIMEOUT,
    PEERINGDB_DEFAULT_URL,
)
from netbox_peering_manager.services.exceptions import (
    PeeringDBAPIError,
    PeeringDBNotFoundError,
    PeeringDBRateLimitError,
)
from netbox_peering_manager.version import __version__

logger = logging.getLogger(__name__)


def get_plugin_config(key: str, default=None):
    """Get plugin configuration value."""
    from django.conf import settings

    plugin_settings = settings.PLUGINS_CONFIG.get("netbox_peering_manager", {})
    return plugin_settings.get(key, default)


class PeeringDBClient:
    """Client for PeeringDB REST API with rate limiting.

    Rate limits per PeeringDB docs:
    - Authenticated: 40 requests/minute
    - Anonymous: 20 requests/minute
    - General: 1 request/second minimum, recommended 2+ seconds between queries
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
        rate_limit: float | None = None,
    ):
        self.base_url = base_url or get_plugin_config("peeringdb_url") or PEERINGDB_DEFAULT_URL
        self.api_key = api_key or get_plugin_config("peeringdb_api_key")
        self.timeout = timeout or get_plugin_config("peeringdb_timeout") or PEERINGDB_DEFAULT_TIMEOUT
        self.rate_limit = (
            rate_limit
            if rate_limit is not None
            else (get_plugin_config("peeringdb_rate_limit") or PEERINGDB_DEFAULT_RATE_LIMIT)
        )
        self._last_request_time: float = 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"netbox-peering-manager/{__version__}"
        if self.api_key:
            self.session.headers["Authorization"] = f"Api-Key {self.api_key}"

    def _enforce_rate_limit(self) -> None:
        """Enforce minimum interval between API requests."""
        if self.rate_limit <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, PeeringDBRateLimitError)),
        reraise=True,
    )
    def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make API request with retry logic and rate limiting."""
        self._enforce_rate_limit()
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.debug(f"PeeringDB request: {url}")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            self._last_request_time = time.monotonic()

            # Handle rate limiting (429) with Retry-After header
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"PeeringDB rate limited, waiting {retry_after}s")
                time.sleep(retry_after)
                raise PeeringDBRateLimitError(retry_after)

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

    def get_ixlan_prefixes_batch(self, ixlan_ids: list[int]) -> list[dict]:
        """Fetch prefixes for multiple IXLANs in a single request.

        Uses PeeringDB's __in filter to batch requests.
        """
        if not ixlan_ids:
            return []
        # PeeringDB supports comma-separated IDs for __in queries
        ids_param = ",".join(str(id) for id in ixlan_ids)
        data = self._request("ixpfx", params={"ixlan_id__in": ids_param})
        return data.get("data", [])

    def get_netixlans(self, ixlan_id: int) -> list[dict]:
        """Fetch all network connections on an IXLAN (peers)."""
        data = self._request("netixlan", params={"ixlan_id": ixlan_id})
        return data.get("data", [])

    def get_netixlans_batch(self, ixlan_ids: list[int]) -> list[dict]:
        """Fetch all network connections for multiple IXLANs in a single request.

        Uses PeeringDB's __in filter to batch requests, significantly reducing
        API calls for IXes with multiple IXLANs.
        """
        if not ixlan_ids:
            return []
        # PeeringDB supports comma-separated IDs for __in queries
        ids_param = ",".join(str(id) for id in ixlan_ids)
        data = self._request("netixlan", params={"ixlan_id__in": ids_param})
        return data.get("data", [])

    def get_network(self, asn: int) -> dict:
        """Fetch network details by ASN."""
        data = self._request("net", params={"asn": asn})
        if not data.get("data"):
            msg = f"Network AS{asn} not found"
            raise PeeringDBNotFoundError(msg)
        return data["data"][0]

    def get_networks_batch(self, asns: list[int]) -> list[dict]:
        """Fetch multiple networks by ASN in a single request.

        Uses PeeringDB's __in filter. Recommended to batch up to 150 ASNs
        per request per PeeringDB documentation.
        """
        if not asns:
            return []
        # PeeringDB supports comma-separated ASNs for __in queries
        asns_param = ",".join(str(asn) for asn in asns)
        data = self._request("net", params={"asn__in": asns_param})
        return data.get("data", [])

    def search_ix(self, query: str) -> list[dict]:
        """Search IXes by name."""
        data = self._request("ix", params={"name__contains": query})
        return data.get("data", [])
