"""Tests for background jobs."""

from unittest.mock import MagicMock, patch

from core.choices import JobStatusChoices
from django.test import TestCase

from netbox_peering_manager.irr_client import IRRClientError
from netbox_peering_manager.jobs import SyncAllPrefixListsJob, SyncPrefixListJob
from netbox_peering_manager.models import IRRSource, PrefixList, PrefixListRule


class SyncPrefixListJobTestCase(TestCase):
    """Test cases for SyncPrefixListJob."""

    def setUp(self):
        """Set up test fixtures."""
        self.irr_source = IRRSource.objects.create(
            name="Test IRR",
            slug="test-irr",
            url="http://fastbgpq4.example.com/",
            enabled=True,
        )
        self.prefix_list = PrefixList.objects.create(
            name="Test Prefix List",
            family=4,  # IPv4
            source_as_set="AS-TEST",
            irr_source=self.irr_source,
        )

    def _create_mock_job(self, obj):
        """Create a mock job object."""
        job = MagicMock()
        job.object = obj
        job.data = {}
        job.status = JobStatusChoices.STATUS_RUNNING
        return job

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_success(self, mock_client_class):
        """Test successful prefix list sync."""
        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24", "198.51.100.0/24"]
        mock_client_class.return_value = mock_client

        runner = SyncPrefixListJob()
        runner.job = self._create_mock_job(self.prefix_list)

        runner.run()

        # Verify IRRClient was called correctly
        mock_client.fetch_prefixes.assert_called_once_with("AS-TEST", 4)

        # Verify rules were created
        rules = PrefixListRule.objects.filter(prefix_list=self.prefix_list)
        self.assertEqual(rules.count(), 2)

        # Verify job data was updated
        self.assertEqual(runner.job.data["created_rules"], 2)
        self.assertEqual(runner.job.data["prefixes"], 2)
        self.assertEqual(runner.job.data["as_set"], "AS-TEST")

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_replaces_existing_rules(self, mock_client_class):
        """Test that sync replaces existing rules."""
        # Create existing rules
        PrefixListRule.objects.create(
            prefix_list=self.prefix_list,
            index=10,
            action="permit",
            prefix_custom="10.0.0.0/8",
        )
        PrefixListRule.objects.create(
            prefix_list=self.prefix_list,
            index=20,
            action="permit",
            prefix_custom="172.16.0.0/12",
        )

        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24"]
        mock_client_class.return_value = mock_client

        runner = SyncPrefixListJob()
        runner.job = self._create_mock_job(self.prefix_list)

        runner.run()

        # Verify old rules were deleted and new ones created
        rules = PrefixListRule.objects.filter(prefix_list=self.prefix_list)
        self.assertEqual(rules.count(), 1)
        self.assertEqual(runner.job.data["deleted_rules"], 2)
        self.assertEqual(runner.job.data["created_rules"], 1)

    def test_sync_non_irr_managed_fails(self):
        """Test that non-IRR-managed prefix list fails."""
        non_irr_prefix_list = PrefixList.objects.create(
            name="Non-IRR Prefix List",
            family=4,
        )

        runner = SyncPrefixListJob()
        runner.job = self._create_mock_job(non_irr_prefix_list)

        runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("not IRR-managed", runner.job.data["error"])

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_irr_error(self, mock_client_class):
        """Test handling of IRR client errors."""
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = IRRClientError("Connection failed")
        mock_client_class.return_value = mock_client

        runner = SyncPrefixListJob()
        runner.job = self._create_mock_job(self.prefix_list)

        with self.assertRaises(IRRClientError):
            runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("Connection failed", runner.job.data["error"])


class SyncAllPrefixListsJobTestCase(TestCase):
    """Test cases for SyncAllPrefixListsJob."""

    def setUp(self):
        """Set up test fixtures."""
        self.irr_source = IRRSource.objects.create(
            name="Test IRR",
            slug="test-irr",
            url="http://fastbgpq4.example.com/",
            enabled=True,
        )
        self.prefix_list1 = PrefixList.objects.create(
            name="Prefix List 1",
            family=4,
            source_as_set="AS-TEST1",
            irr_source=self.irr_source,
        )
        self.prefix_list2 = PrefixList.objects.create(
            name="Prefix List 2",
            family=6,  # IPv6
            source_as_set="AS-TEST2",
            irr_source=self.irr_source,
        )

    def _create_mock_job(self, obj):
        """Create a mock job object."""
        job = MagicMock()
        job.object = obj
        job.data = {}
        job.status = JobStatusChoices.STATUS_RUNNING
        return job

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_all_success(self, mock_client_class):
        """Test successful sync of all prefix lists."""
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],  # First prefix list
            ["2001:db8::/32"],  # Second prefix list
        ]
        mock_client_class.return_value = mock_client

        runner = SyncAllPrefixListsJob()
        runner.job = self._create_mock_job(self.irr_source)

        runner.run()

        # Verify both prefix lists were synced
        self.assertEqual(runner.job.data["synced"], 2)
        self.assertEqual(runner.job.data["failed"], 0)
        self.assertEqual(runner.job.data["total_prefix_lists"], 2)

        # Verify rules were created for both
        self.assertEqual(PrefixListRule.objects.filter(prefix_list=self.prefix_list1).count(), 1)
        self.assertEqual(PrefixListRule.objects.filter(prefix_list=self.prefix_list2).count(), 1)

    def test_sync_disabled_source_fails(self):
        """Test that disabled IRR source fails."""
        self.irr_source.enabled = False
        self.irr_source.save()

        runner = SyncAllPrefixListsJob()
        runner.job = self._create_mock_job(self.irr_source)

        runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("disabled", runner.job.data["error"])

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_partial_failure(self, mock_client_class):
        """Test handling of partial failures."""
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],  # First succeeds
            IRRClientError("AS-SET not found"),  # Second fails
        ]
        mock_client_class.return_value = mock_client

        runner = SyncAllPrefixListsJob()
        runner.job = self._create_mock_job(self.irr_source)

        runner.run()

        # Job should complete but with errors noted
        self.assertEqual(runner.job.data["synced"], 1)
        self.assertEqual(runner.job.data["failed"], 1)
        self.assertEqual(len(runner.job.data["errors"]), 1)
        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_skips_non_irr_managed(self, mock_client_class):
        """Test that non-IRR-managed prefix lists are skipped."""
        # Create a non-IRR-managed prefix list
        PrefixList.objects.create(
            name="Non-IRR Prefix List",
            family=4,
        )

        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],
            ["2001:db8::/32"],
        ]
        mock_client_class.return_value = mock_client

        runner = SyncAllPrefixListsJob()
        runner.job = self._create_mock_job(self.irr_source)

        runner.run()

        # Only the 2 IRR-managed prefix lists should be synced
        self.assertEqual(runner.job.data["total_prefix_lists"], 2)
        self.assertEqual(mock_client.fetch_prefixes.call_count, 2)
