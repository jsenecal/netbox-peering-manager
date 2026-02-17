"""Tests for background jobs."""

from unittest.mock import MagicMock, patch

from core.choices import JobStatusChoices
from django.test import TestCase
from netbox_routing.models import PrefixList, PrefixListEntry

from netbox_peering_manager.irr_client import IRRClientError
from netbox_peering_manager.jobs import FAMILY_MAP, SyncAllPrefixListsJob, SyncPrefixListJob
from netbox_peering_manager.models import IRRPrefixListConfig, IRRSource


class SyncPrefixListJobTestCase(TestCase):
    """Test cases for SyncPrefixListJob."""

    def setUp(self):
        self.irr_source = IRRSource.objects.create(
            name="Test IRR",
            slug="test-irr",
            url="http://fastbgpq4.example.com/",
            enabled=True,
        )
        self.prefix_list = PrefixList.objects.create(
            name="Test Prefix List",
            family=4,
        )
        self.config = IRRPrefixListConfig.objects.create(
            prefix_list=self.prefix_list,
            irr_source=self.irr_source,
            source_as_set="AS-TEST",
        )

    def _create_mock_job(self, obj):
        job = MagicMock()
        job.object = obj
        job.data = {}
        job.status = JobStatusChoices.STATUS_RUNNING
        job.log = MagicMock()
        return job

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24", "198.51.100.0/24"]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.config)
        runner = SyncPrefixListJob(mock_job)

        runner.run()

        mock_client.fetch_prefixes.assert_called_once_with("AS-TEST", "ipv4")

        entries = PrefixListEntry.objects.filter(prefix_list=self.prefix_list)
        self.assertEqual(entries.count(), 2)

        self.assertEqual(runner.job.data["created_entries"], 2)
        self.assertEqual(runner.job.data["prefixes"], 2)
        self.assertEqual(runner.job.data["as_set"], "AS-TEST")

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_replaces_existing_entries(self, mock_client_class):
        PrefixListEntry.objects.create(prefix_list=self.prefix_list, sequence=10, action="permit", prefix="10.0.0.0/8")
        PrefixListEntry.objects.create(
            prefix_list=self.prefix_list, sequence=20, action="permit", prefix="172.16.0.0/12"
        )

        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24"]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.config)
        runner = SyncPrefixListJob(mock_job)

        runner.run()

        entries = PrefixListEntry.objects.filter(prefix_list=self.prefix_list)
        self.assertEqual(entries.count(), 1)
        self.assertEqual(runner.job.data["deleted_entries"], 2)
        self.assertEqual(runner.job.data["created_entries"], 1)

    def test_sync_non_irr_managed_fails(self):
        non_irr_pl = PrefixList.objects.create(name="Non-IRR PL", family=4)
        non_irr_config = IRRPrefixListConfig.objects.create(prefix_list=non_irr_pl)

        mock_job = self._create_mock_job(non_irr_config)
        runner = SyncPrefixListJob(mock_job)

        runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("not IRR-managed", runner.job.data["error"])

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_irr_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = IRRClientError("Connection failed")
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.config)
        runner = SyncPrefixListJob(mock_job)

        with self.assertRaises(IRRClientError):
            runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("Connection failed", runner.job.data["error"])

    def test_family_map_ipv4(self):
        """FAMILY_MAP converts integer 4 to string 'ipv4'."""
        self.assertEqual(FAMILY_MAP[4], "ipv4")

    def test_family_map_ipv6(self):
        """FAMILY_MAP converts integer 6 to string 'ipv6'."""
        self.assertEqual(FAMILY_MAP[6], "ipv6")

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_ipv6_family_conversion(self, mock_client_class):
        """Verify that family=6 prefix lists pass 'ipv6' to fetch_prefixes."""
        ipv6_pl = PrefixList.objects.create(name="IPv6 PL", family=6)
        ipv6_config = IRRPrefixListConfig.objects.create(
            prefix_list=ipv6_pl,
            irr_source=self.irr_source,
            source_as_set="AS-IPV6TEST",
        )

        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["2001:db8::/32"]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(ipv6_config)
        runner = SyncPrefixListJob(mock_job)
        runner.run()

        mock_client.fetch_prefixes.assert_called_once_with("AS-IPV6TEST", "ipv6")
        self.assertEqual(runner.job.data["family"], "ipv6")

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_atomic_rollback_on_bulk_create_failure(self, mock_client_class):
        """Verify entries are not deleted if bulk_create fails (atomic rollback)."""
        # Pre-populate entries
        PrefixListEntry.objects.create(prefix_list=self.prefix_list, sequence=10, action="permit", prefix="10.0.0.0/8")
        PrefixListEntry.objects.create(
            prefix_list=self.prefix_list, sequence=20, action="permit", prefix="172.16.0.0/12"
        )
        self.assertEqual(PrefixListEntry.objects.filter(prefix_list=self.prefix_list).count(), 2)

        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24"]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.config)
        runner = SyncPrefixListJob(mock_job)

        # Patch bulk_create to raise an exception inside the atomic block
        with (
            patch.object(PrefixListEntry.objects, "bulk_create", side_effect=RuntimeError("DB error")),
            self.assertRaises(RuntimeError),
        ):
            runner.run()

        # Original entries should still exist due to atomic rollback
        self.assertEqual(PrefixListEntry.objects.filter(prefix_list=self.prefix_list).count(), 2)


class SyncAllPrefixListsJobTestCase(TestCase):
    """Test cases for SyncAllPrefixListsJob."""

    def setUp(self):
        self.irr_source = IRRSource.objects.create(
            name="Test IRR",
            slug="test-irr",
            url="http://fastbgpq4.example.com/",
            enabled=True,
        )
        self.prefix_list1 = PrefixList.objects.create(name="Prefix List 1", family=4)
        self.prefix_list2 = PrefixList.objects.create(name="Prefix List 2", family=6)
        self.config1 = IRRPrefixListConfig.objects.create(
            prefix_list=self.prefix_list1, irr_source=self.irr_source, source_as_set="AS-TEST1"
        )
        self.config2 = IRRPrefixListConfig.objects.create(
            prefix_list=self.prefix_list2, irr_source=self.irr_source, source_as_set="AS-TEST2"
        )

    def _create_mock_job(self, obj):
        job = MagicMock()
        job.object = obj
        job.data = {}
        job.status = JobStatusChoices.STATUS_RUNNING
        job.log = MagicMock()
        return job

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_all_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],
            ["2001:db8::/32"],
        ]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)

        runner.run()

        self.assertEqual(runner.job.data["synced"], 2)
        self.assertEqual(runner.job.data["failed"], 0)
        self.assertEqual(runner.job.data["total_configs"], 2)

        self.assertEqual(PrefixListEntry.objects.filter(prefix_list=self.prefix_list1).count(), 1)
        self.assertEqual(PrefixListEntry.objects.filter(prefix_list=self.prefix_list2).count(), 1)

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_all_uses_string_family(self, mock_client_class):
        """Verify SyncAllPrefixListsJob converts integer family to string for each config."""
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],
            ["2001:db8::/32"],
        ]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)
        runner.run()

        # prefix_list1 has family=4, prefix_list2 has family=6
        calls = mock_client.fetch_prefixes.call_args_list
        family_args = [call[0][1] for call in calls]
        self.assertIn("ipv4", family_args)
        self.assertIn("ipv6", family_args)

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_all_atomic_rollback(self, mock_client_class):
        """Verify entries not deleted if bulk_create fails in SyncAllPrefixListsJob."""
        PrefixListEntry.objects.create(prefix_list=self.prefix_list1, sequence=10, action="permit", prefix="10.0.0.0/8")

        mock_client = MagicMock()
        mock_client.fetch_prefixes.return_value = ["192.0.2.0/24"]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)

        # Patch bulk_create to fail
        with patch.object(PrefixListEntry.objects, "bulk_create", side_effect=Exception("DB error")):
            runner.run()

        # Original entry should still exist due to atomic rollback
        self.assertEqual(PrefixListEntry.objects.filter(prefix_list=self.prefix_list1).count(), 1)
        # Both configs should be counted as failed
        self.assertEqual(runner.job.data["failed"], 2)

    def test_sync_disabled_source_fails(self):
        self.irr_source.enabled = False
        self.irr_source.save()

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)

        runner.run()

        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn("disabled", runner.job.data["error"])

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_partial_failure(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],
            IRRClientError("AS-SET not found"),
        ]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)

        runner.run()

        self.assertEqual(runner.job.data["synced"], 1)
        self.assertEqual(runner.job.data["failed"], 1)
        self.assertEqual(len(runner.job.data["errors"]), 1)
        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_ERRORED)

    @patch("netbox_peering_manager.jobs.IRRClient")
    def test_sync_skips_non_irr_managed(self, mock_client_class):
        # Create a non-IRR-managed config
        non_irr_pl = PrefixList.objects.create(name="Non-IRR PL", family=4)
        IRRPrefixListConfig.objects.create(prefix_list=non_irr_pl)

        mock_client = MagicMock()
        mock_client.fetch_prefixes.side_effect = [
            ["192.0.2.0/24"],
            ["2001:db8::/32"],
        ]
        mock_client_class.return_value = mock_client

        mock_job = self._create_mock_job(self.irr_source)
        runner = SyncAllPrefixListsJob(mock_job)

        runner.run()

        # Only the 2 IRR-managed configs should be synced
        self.assertEqual(runner.job.data["total_configs"], 2)
        self.assertEqual(mock_client.fetch_prefixes.call_count, 2)
