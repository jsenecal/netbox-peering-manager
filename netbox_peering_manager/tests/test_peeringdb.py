"""Tests for PeeringDB integration."""

from unittest.mock import MagicMock, patch

from dcim.models import Site
from django.test import TestCase
from ipam.models import Prefix

from netbox_peering_manager.models import (
    PeeringDBPeer,
    PeeringFabric,
    PeeringFabricPeeringDB,
    PeeringNetwork,
    PeeringNetworkPeeringDB,
)
from netbox_peering_manager.services.peeringdb import PeeringDBClient
from netbox_peering_manager.services.peeringdb_sync import (
    PeeringDBSyncService,
    SyncResult,
    link_fabric_to_peeringdb,
)


class PeeringDBClientTestCase(TestCase):
    """Test PeeringDB API client with mocked responses."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = PeeringDBClient(
            base_url="https://peeringdb.example.com/api",
            api_key="test-api-key",
            timeout=30,
        )

    @patch("netbox_peering_manager.services.peeringdb.requests.Session")
    def test_get_ix(self, mock_session_class):
        """Test fetching IX details by ID."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": 123,
                    "name": "AMS-IX",
                    "city": "Amsterdam",
                    "country": "NL",
                    "website": "https://www.ams-ix.net",
                    "tech_email": "noc@ams-ix.net",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create fresh client to use mock
        client = PeeringDBClient(
            base_url="https://peeringdb.example.com/api",
            api_key="test-api-key",
        )

        result = client.get_ix(123)

        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "AMS-IX")
        self.assertEqual(result["city"], "Amsterdam")
        self.assertEqual(result["country"], "NL")

    @patch("netbox_peering_manager.services.peeringdb.requests.Session")
    def test_search_ix(self, mock_session_class):
        """Test searching for IXes by name."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": 123, "name": "AMS-IX"},
                {"id": 456, "name": "AMS-IX Caribbean"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PeeringDBClient(
            base_url="https://peeringdb.example.com/api",
        )

        results = client.search_ix("AMS")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "AMS-IX")
        self.assertEqual(results[1]["name"], "AMS-IX Caribbean")

    @patch("netbox_peering_manager.services.peeringdb.requests.Session")
    def test_get_ixlans(self, mock_session_class):
        """Test fetching IXLANs for an IX."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": 100,
                    "ix_id": 123,
                    "name": "Production VLAN",
                    "mtu": 1500,
                    "rs_asn": 65000,
                    "dot1q_support": True,
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PeeringDBClient(base_url="https://peeringdb.example.com/api")

        results = client.get_ixlans(123)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 100)
        self.assertEqual(results[0]["name"], "Production VLAN")

    @patch("netbox_peering_manager.services.peeringdb.requests.Session")
    def test_get_netixlans(self, mock_session_class):
        """Test fetching network connections on an IXLAN."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "asn": 65001,
                    "name": "Test Network 1",
                    "ipaddr4": "192.0.2.1",
                    "ipaddr6": "2001:db8::1",
                    "speed": 10000,
                    "is_rs_peer": True,
                },
                {
                    "asn": 65002,
                    "name": "Test Network 2",
                    "ipaddr4": "192.0.2.2",
                    "ipaddr6": None,
                    "speed": 1000,
                    "is_rs_peer": False,
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PeeringDBClient(base_url="https://peeringdb.example.com/api")

        results = client.get_netixlans(100)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["asn"], 65001)
        self.assertEqual(results[1]["asn"], 65002)


class PeeringDBSyncServiceTestCase(TestCase):
    """Test PeeringDB sync service logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.fabric = PeeringFabric.objects.create(
            name="Test IX",
            slug="test-ix",
            site=self.site,
        )

    def test_sync_fabric_without_peeringdb_link(self):
        """Test sync fails gracefully when fabric has no PeeringDB link."""
        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric)

        self.assertFalse(result.success)
        self.assertIn("Fabric is not linked to PeeringDB", result.errors)

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_netixlans")
    def test_sync_fabric_updates_peeringdb_info(self, mock_get_netixlans, mock_get_ixlans, mock_get_ix):
        """Test sync updates IX details from PeeringDB."""
        # Link fabric to PeeringDB
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=123,
        )

        # Mock API responses
        mock_get_ix.return_value = {
            "id": 123,
            "name": "Updated IX Name",
            "city": "New City",
            "country": "US",
            "website": "https://updated.example.com",
            "tech_email": "new@example.com",
        }
        mock_get_ixlans.return_value = []
        mock_get_netixlans.return_value = []

        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric)

        self.assertTrue(result.success)
        self.assertTrue(result.fabric_updated)

        # Verify PeeringDB info was updated
        self.fabric.refresh_from_db()
        pdb_info = self.fabric.peeringdb
        self.assertEqual(pdb_info.name, "Updated IX Name")
        self.assertEqual(pdb_info.city, "New City")
        self.assertEqual(pdb_info.country, "US")

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_ixlan_prefixes")
    @patch.object(PeeringDBClient, "get_netixlans")
    def test_sync_fabric_creates_network(
        self,
        mock_get_netixlans,
        mock_get_ixlan_prefixes,
        mock_get_ixlans,
        mock_get_ix,
    ):
        """Test sync creates PeeringNetwork from IXLAN data."""
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=123,
        )

        mock_get_ix.return_value = {
            "id": 123,
            "name": "Test IX",
            "city": "City",
            "country": "US",
        }
        mock_get_ixlans.return_value = [
            {
                "id": 100,
                "name": "Production LAN",
                "mtu": 9000,
                "rs_asn": 65000,
                "dot1q_support": False,
            }
        ]
        mock_get_ixlan_prefixes.return_value = [
            {"prefix": "192.0.2.0/24"},
        ]
        mock_get_netixlans.return_value = []

        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric)

        self.assertTrue(result.success)
        self.assertEqual(result.networks_created, 1)

        # Verify network was created
        network = PeeringNetwork.objects.get(fabric=self.fabric)
        self.assertEqual(network.name, "Production LAN")
        self.assertTrue(hasattr(network, "peeringdb"))
        self.assertEqual(network.peeringdb.ixlan_id, 100)
        self.assertEqual(network.peeringdb.mtu, 9000)

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_netixlans")
    def test_sync_fabric_matches_existing_network(self, mock_get_netixlans, mock_get_ixlans, mock_get_ix):
        """Test sync matches existing network by IXLAN ID."""
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=123,
        )

        # Create existing network with PeeringDB link
        prefix = Prefix.objects.create(prefix="192.0.2.0/24")
        network = PeeringNetwork.objects.create(
            fabric=self.fabric,
            name="Existing Network",
            prefix=prefix,
        )
        PeeringNetworkPeeringDB.objects.create(
            network=network,
            ixlan_id=100,
            name="Old Name",
        )

        mock_get_ix.return_value = {
            "id": 123,
            "name": "Test IX",
            "city": "City",
            "country": "US",
        }
        mock_get_ixlans.return_value = [
            {
                "id": 100,
                "name": "Updated LAN Name",
                "mtu": 9000,
                "rs_asn": 65000,
                "dot1q_support": True,
            }
        ]
        mock_get_netixlans.return_value = []

        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric)

        self.assertTrue(result.success)
        self.assertEqual(result.networks_updated, 1)
        self.assertEqual(result.networks_created, 0)

        # Verify network was updated
        network.refresh_from_db()
        self.assertEqual(network.peeringdb.name, "Updated LAN Name")
        self.assertEqual(network.peeringdb.mtu, 9000)
        self.assertTrue(network.peeringdb.dot1q_support)

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_netixlans")
    @patch(
        "netbox_peering_manager.services.peeringdb_sync.get_plugin_config",
        return_value=[65001],
    )
    def test_sync_fabric_creates_peers(
        self,
        mock_get_plugin_config,
        mock_get_netixlans,
        mock_get_ixlans,
        mock_get_ix,
    ):
        """Test sync creates peer records, filtering local ASNs."""
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=123,
        )

        mock_get_ix.return_value = {
            "id": 123,
            "name": "Test IX",
            "city": "City",
            "country": "US",
        }
        mock_get_ixlans.return_value = [
            {"id": 100, "name": "LAN"},
        ]
        mock_get_netixlans.return_value = [
            {
                "asn": 65001,  # Local ASN - should be filtered
                "name": "Our Network",
                "ipaddr4": "192.0.2.1",
                "ipaddr6": "2001:db8::1",
                "speed": 10000,
                "is_rs_peer": False,
            },
            {
                "asn": 65002,  # Remote ASN - should be created
                "name": "Remote Network",
                "ipaddr4": "192.0.2.2",
                "ipaddr6": "2001:db8::2",
                "speed": 10000,
                "is_rs_peer": True,
            },
            {
                "asn": 65003,  # Another remote ASN
                "name": "Another Network",
                "ipaddr4": "192.0.2.3",
                "ipaddr6": None,
                "speed": 1000,
                "is_rs_peer": False,
            },
        ]

        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric, peers_only=True)

        self.assertTrue(result.success)
        self.assertEqual(result.peers_synced, 2)  # Only non-local ASNs

        # Verify peers were created correctly
        peers = PeeringDBPeer.objects.filter(fabric=self.fabric)
        self.assertEqual(peers.count(), 2)

        peer_asns = set(peers.values_list("asn", flat=True))
        self.assertNotIn(65001, peer_asns)  # Local ASN filtered
        self.assertIn(65002, peer_asns)
        self.assertIn(65003, peer_asns)

        # Verify peer details
        peer_65002 = peers.get(asn=65002)
        self.assertEqual(peer_65002.name, "Remote Network")
        self.assertEqual(peer_65002.ipv4_addr, "192.0.2.2")
        self.assertEqual(peer_65002.ipv6_addr, "2001:db8::2")
        self.assertTrue(peer_65002.is_rs_peer)

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_netixlans")
    @patch(
        "netbox_peering_manager.services.peeringdb_sync.get_plugin_config",
        return_value=[],
    )
    def test_sync_fabric_clears_old_peers(
        self,
        mock_get_plugin_config,
        mock_get_netixlans,
        mock_get_ixlans,
        mock_get_ix,
    ):
        """Test sync clears existing peers before creating new ones."""
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=123,
        )

        # Create existing peer that should be removed
        PeeringDBPeer.objects.create(
            fabric=self.fabric,
            asn=65999,
            name="Old Peer",
            ipv4_addr="192.0.2.99",
        )

        mock_get_ix.return_value = {"id": 123, "name": "Test IX"}
        mock_get_ixlans.return_value = [{"id": 100}]
        mock_get_netixlans.return_value = [
            {
                "asn": 65001,
                "name": "New Peer",
                "ipaddr4": "192.0.2.1",
                "ipaddr6": None,
                "speed": 10000,
                "is_rs_peer": False,
            }
        ]

        service = PeeringDBSyncService()
        result = service.sync_fabric(self.fabric, peers_only=True)

        self.assertTrue(result.success)

        # Verify old peer was removed
        self.assertFalse(PeeringDBPeer.objects.filter(asn=65999).exists())

        # Verify new peer was created
        self.assertTrue(PeeringDBPeer.objects.filter(asn=65001).exists())


class LinkFabricToPeeringDBTestCase(TestCase):
    """Test link_fabric_to_peeringdb helper function."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.fabric = PeeringFabric.objects.create(
            name="Test IX",
            slug="test-ix",
            site=self.site,
        )

    def test_link_creates_peeringdb_info(self):
        """Test linking creates PeeringFabricPeeringDB model."""
        result = link_fabric_to_peeringdb(self.fabric, ix_id=123, sync=False)

        self.assertIsInstance(result, PeeringFabricPeeringDB)
        self.assertEqual(result.ix_id, 123)
        self.assertEqual(result.fabric, self.fabric)

        # Verify it's accessible from fabric
        self.assertTrue(hasattr(self.fabric, "peeringdb"))
        self.assertEqual(self.fabric.peeringdb.ix_id, 123)

    def test_link_updates_existing_peeringdb_info(self):
        """Test linking updates existing PeeringFabricPeeringDB if present."""
        # Create existing link
        PeeringFabricPeeringDB.objects.create(
            fabric=self.fabric,
            ix_id=100,
        )

        result = link_fabric_to_peeringdb(self.fabric, ix_id=200, sync=False)

        self.assertIsInstance(result, PeeringFabricPeeringDB)
        self.assertEqual(result.ix_id, 200)

        # Verify only one link exists
        self.assertEqual(PeeringFabricPeeringDB.objects.filter(fabric=self.fabric).count(), 1)

    @patch.object(PeeringDBSyncService, "sync_fabric")
    def test_link_without_sync(self, mock_sync_fabric):
        """Test sync=False skips sync operation."""
        result = link_fabric_to_peeringdb(self.fabric, ix_id=123, sync=False)

        self.assertIsInstance(result, PeeringFabricPeeringDB)
        mock_sync_fabric.assert_not_called()

    @patch.object(PeeringDBClient, "get_ix")
    @patch.object(PeeringDBClient, "get_ixlans")
    @patch.object(PeeringDBClient, "get_netixlans")
    def test_link_with_sync(self, mock_get_netixlans, mock_get_ixlans, mock_get_ix):
        """Test sync=True performs sync after linking."""
        mock_get_ix.return_value = {
            "id": 123,
            "name": "Synced IX",
            "city": "City",
            "country": "US",
        }
        mock_get_ixlans.return_value = []
        mock_get_netixlans.return_value = []

        result = link_fabric_to_peeringdb(self.fabric, ix_id=123, sync=True)

        self.assertIsInstance(result, SyncResult)
        self.assertTrue(result.success)
        self.assertTrue(result.fabric_updated)

        # Verify sync updated the PeeringDB info
        self.fabric.refresh_from_db()
        self.assertEqual(self.fabric.peeringdb.name, "Synced IX")
