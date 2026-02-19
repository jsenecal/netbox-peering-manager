"""Tests for IRRClient."""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from netbox_peering_manager.irr_client import IRRClient, IRRClientError


class IRRClientTestCase(TestCase):
    """Test cases for IRRClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.irr_source = MagicMock()
        self.irr_source.url = "http://fastbgpq4.example.com/"
        self.irr_source.sources = "RIPE,RADB"
        self.irr_source.cache_ttl = 3600

        self.client = IRRClient(self.irr_source)

    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.base_url, "http://fastbgpq4.example.com")
        self.assertEqual(self.client.irr_source, self.irr_source)

    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes are stripped from URL."""
        self.irr_source.url = "http://example.com///"
        client = IRRClient(self.irr_source)
        self.assertEqual(client.base_url, "http://example.com")

    def test_build_params_ipv4(self):
        """Test parameter building for IPv4."""
        params = self.client._build_params("AS-TEST", "ipv4")

        self.assertEqual(params["target"], "AS-TEST")
        self.assertEqual(params["format"], "json")
        self.assertEqual(params["sources"], "RIPE,RADB")
        self.assertEqual(params["cache_ttl"], 3600)
        self.assertEqual(params["protocol"], 4)
        self.assertNotIn("protocol", {k: v for k, v in params.items() if v == 6})

    def test_build_params_ipv6(self):
        """Test parameter building for IPv6."""
        params = self.client._build_params("AS-TEST", "ipv6")

        self.assertEqual(params["target"], "AS-TEST")
        self.assertEqual(params["protocol"], 6)

    def test_build_params_no_sources(self):
        """Test parameter building when no sources configured."""
        self.irr_source.sources = ""
        self.irr_source.cache_ttl = None
        client = IRRClient(self.irr_source)

        params = client._build_params("AS-TEST", "ipv4")

        self.assertNotIn("sources", params)
        self.assertNotIn("cache_ttl", params)

    @patch.object(IRRClient, "_fetch_family")
    def test_fetch_prefixes_ipv4_only(self, mock_fetch):
        """Test fetching only IPv4 prefixes."""
        mock_fetch.return_value = ["192.0.2.0/24", "198.51.100.0/24"]

        result = self.client.fetch_prefixes("AS-TEST", "ipv4")

        mock_fetch.assert_called_once_with("AS-TEST", "ipv4")
        self.assertEqual(result, ["192.0.2.0/24", "198.51.100.0/24"])

    @patch.object(IRRClient, "_fetch_family")
    def test_fetch_prefixes_ipv6_only(self, mock_fetch):
        """Test fetching only IPv6 prefixes."""
        mock_fetch.return_value = ["2001:db8::/32"]

        result = self.client.fetch_prefixes("AS-TEST", "ipv6")

        mock_fetch.assert_called_once_with("AS-TEST", "ipv6")
        self.assertEqual(result, ["2001:db8::/32"])

    @patch.object(IRRClient, "_fetch_family")
    def test_fetch_prefixes_both_families(self, mock_fetch):
        """Test fetching both address families."""
        mock_fetch.side_effect = [
            ["192.0.2.0/24"],  # IPv4 call
            ["2001:db8::/32"],  # IPv6 call
        ]

        result = self.client.fetch_prefixes("AS-TEST", "both")

        self.assertEqual(mock_fetch.call_count, 2)
        self.assertEqual(result, ["192.0.2.0/24", "2001:db8::/32"])

    @patch("netbox_peering_manager.irr_client.httpx.Client")
    def test_fetch_family_synchronous(self, mock_client_class):
        """Test synchronous prefix fetching."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"nn": ["192.0.2.0/24", "198.51.100.0/24"]}}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = self.client._fetch_family("AS-TEST", "ipv4")

        self.assertEqual(result, ["192.0.2.0/24", "198.51.100.0/24"])

    @patch("netbox_peering_manager.irr_client.httpx.Client")
    def test_fetch_family_empty_response(self, mock_client_class):
        """Test handling of empty response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {}}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = self.client._fetch_family("AS-TEST", "ipv4")

        self.assertEqual(result, [])

    @patch("netbox_peering_manager.irr_client.time.sleep")
    @patch("netbox_peering_manager.irr_client.httpx.Client")
    def test_fetch_family_async_mode(self, mock_client_class, mock_sleep):
        """Test async job polling."""
        # First response: 202 with job_id
        async_response = MagicMock()
        async_response.status_code = 202
        async_response.json.return_value = {"job_id": "test-job-123"}

        # Poll responses: pending, then completed
        pending_response = MagicMock()
        pending_response.json.return_value = {"status": "pending"}
        pending_response.raise_for_status = MagicMock()

        completed_response = MagicMock()
        completed_response.json.return_value = {
            "status": "completed",
            "data": {"nn": ["192.0.2.0/24"]},
        }
        completed_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.side_effect = [async_response, pending_response, completed_response]
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = self.client._fetch_family("AS-TEST", "ipv4")

        self.assertEqual(result, ["192.0.2.0/24"])
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("netbox_peering_manager.irr_client.time.sleep")
    @patch("netbox_peering_manager.irr_client.httpx.Client")
    def test_poll_job_failed(self, mock_client_class, mock_sleep):
        """Test handling of failed async job."""
        async_response = MagicMock()
        async_response.status_code = 202
        async_response.json.return_value = {"job_id": "test-job-123"}

        failed_response = MagicMock()
        failed_response.json.return_value = {
            "status": "failed",
            "error": "AS-SET not found",
        }
        failed_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.side_effect = [async_response, failed_response]
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        with self.assertRaises(IRRClientError) as context:
            self.client._fetch_family("AS-TEST", "ipv4")

        self.assertIn("Job failed", str(context.exception))
        self.assertIn("AS-SET not found", str(context.exception))


class IRRClientErrorTestCase(TestCase):
    """Test cases for IRRClientError."""

    def test_exception_message(self):
        """Test exception carries message."""
        error = IRRClientError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_exception_inheritance(self):
        """Test exception inherits from Exception."""
        error = IRRClientError("test")
        self.assertIsInstance(error, Exception)
