"""
Client for communicating with fastbgpq4 API.
"""

import logging
import time
from typing import Any

import httpx

from netbox_peering_manager.models import IRRSource

logger = logging.getLogger(__name__)

# Configuration defaults
DEFAULT_TIMEOUT = 30.0
POLL_INTERVAL = 2.0
MAX_POLL_ATTEMPTS = 150  # 5 minutes max with 2s interval


class IRRClientError(Exception):
    """Base exception for IRR client errors."""



class IRRClient:
    """Client for querying fastbgpq4 API."""

    def __init__(self, irr_source: IRRSource):
        self.irr_source = irr_source
        self.base_url = irr_source.url.rstrip("/")

    def _build_params(self, as_set: str, family: str) -> dict[str, Any]:
        """Build query parameters for fastbgpq4 API."""
        params = {
            "target": as_set,
            "format": "json",
        }
        if self.irr_source.sources:
            params["sources"] = self.irr_source.sources
        if self.irr_source.cache_ttl:
            params["cache_ttl"] = self.irr_source.cache_ttl

        # Filter by address family
        if family == "ipv4":
            params["max_masklen"] = 32
        elif family == "ipv6":
            params["min_masklen"] = 33  # Only IPv6 prefixes

        return params

    def fetch_prefixes(self, as_set: str, family: str = "both") -> list[str]:
        """
        Fetch prefixes for an AS-SET from fastbgpq4.

        Args:
            as_set: The AS-SET to query (e.g., AS-HURRICANE)
            family: Address family filter (ipv4, ipv6, or both)

        Returns:
            List of prefix strings (e.g., ["192.0.2.0/24", "2001:db8::/32"])
        """
        prefixes = []

        if family in ("ipv4", "both"):
            prefixes.extend(self._fetch_family(as_set, "ipv4"))

        if family in ("ipv6", "both"):
            prefixes.extend(self._fetch_family(as_set, "ipv6"))

        return prefixes

    def _fetch_family(self, as_set: str, family: str) -> list[str]:
        """Fetch prefixes for a specific address family."""
        params = self._build_params(as_set, family)
        url = f"{self.base_url}/api/v1/as-set/expand"

        logger.info(f"Fetching {family} prefixes for {as_set} from {url}")

        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(url, params=params)

            if response.status_code == 202:
                # Async mode - poll for results
                job_data = response.json()
                return self._poll_job(client, job_data["job_id"])

            response.raise_for_status()
            data = response.json()

            # fastbgpq4 returns {"data": {"nn": ["prefix1", "prefix2", ...]}}
            if "data" in data and "nn" in data["data"]:
                return data["data"]["nn"]
            if "data" in data:
                # Handle alternative response format
                return list(data["data"].values())[0] if data["data"] else []

            return []

    def _poll_job(self, client: httpx.Client, job_id: str) -> list[str]:
        """Poll for async job completion."""
        poll_url = f"{self.base_url}/api/v1/jobs/{job_id}"

        for attempt in range(MAX_POLL_ATTEMPTS):
            time.sleep(POLL_INTERVAL)
            response = client.get(poll_url)
            response.raise_for_status()

            job_data = response.json()
            status = job_data.get("status")

            if status == "completed":
                data = job_data.get("data", {})
                if "nn" in data:
                    return data["nn"]
                return list(data.values())[0] if data else []

            if status == "failed":
                error = job_data.get("error", "Unknown error")
                msg = f"Job failed: {error}"
                raise IRRClientError(msg)

            logger.debug(f"Job {job_id} still processing (attempt {attempt + 1})")

        msg = f"Job {job_id} timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s"
        raise IRRClientError(msg)
