"""Tests for ConfigRenderer service."""

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Site
from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress, Prefix

from netbox_peering_manager.models import (
    BFD,
    BGPPeerGroup,
    BGPSession,
    PeeringFabric,
    PeeringNetwork,
    Relationship,
    RoutingPolicy,
)
from netbox_peering_manager.services.config_renderer import ConfigRenderer


class ConfigRendererTestCase(TestCase):
    """Test cases for ConfigRenderer.build_context()."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create site
        cls.site = Site.objects.create(name="Test Site", slug="test-site")

        # Create platform
        cls.platform = Platform.objects.create(name="Junos", slug="junos")

        # Create device infrastructure
        cls.manufacturer = Manufacturer.objects.create(name="Juniper", slug="juniper")
        cls.device_type = DeviceType.objects.create(manufacturer=cls.manufacturer, model="MX480", slug="mx480")
        cls.device_role = DeviceRole.objects.create(name="Router", slug="router")

        # Create devices
        cls.device1 = Device.objects.create(
            name="router1",
            site=cls.site,
            role=cls.device_role,
            device_type=cls.device_type,
            platform=cls.platform,
        )
        cls.device2 = Device.objects.create(
            name="router2",
            site=cls.site,
            role=cls.device_role,
            device_type=cls.device_type,
        )

        # Create RIR and ASNs
        cls.rir = RIR.objects.create(name="Test RIR", slug="test-rir")
        cls.local_as = ASN.objects.create(asn=65000, rir=cls.rir)
        cls.remote_as1 = ASN.objects.create(asn=65001, rir=cls.rir)
        cls.remote_as2 = ASN.objects.create(asn=65002, rir=cls.rir)

        # Create IP addresses
        cls.local_ip1 = IPAddress.objects.create(address="192.0.2.1/32")
        cls.remote_ip1 = IPAddress.objects.create(address="192.0.2.2/32")
        cls.local_ip2 = IPAddress.objects.create(address="192.0.2.3/32")
        cls.remote_ip2 = IPAddress.objects.create(address="192.0.2.4/32")
        cls.local_ip3 = IPAddress.objects.create(address="2001:db8::1/128")
        cls.remote_ip3 = IPAddress.objects.create(address="2001:db8::2/128")

        # Create routing policies
        cls.import_policy = RoutingPolicy.objects.create(
            name="IMPORT-PEER", description="Import policy for peers", weight=100
        )
        cls.export_policy = RoutingPolicy.objects.create(
            name="EXPORT-PEER", description="Export policy for peers", weight=50
        )
        cls.common_policy = RoutingPolicy.objects.create(name="COMMON-POLICY", description="Shared policy", weight=75)

        # Create peer groups
        cls.peer_group1 = BGPPeerGroup.objects.create(name="PEERS", description="Peer sessions")
        cls.peer_group2 = BGPPeerGroup.objects.create(name="TRANSIT", description="Transit sessions")

        # Create relationship
        cls.relationship = Relationship.objects.create(name="Peer", slug="peer", description="Peering relationship")

        # Create BFD profile
        cls.bfd_profile = BFD.objects.create(
            name="fast-bfd",
            minimum_transmit_interval=100,
            minimum_receive_interval=100,
            detect_multiplier=3,
        )

        # Create peering fabric and network
        cls.fabric = PeeringFabric.objects.create(name="DE-CIX Frankfurt", slug="de-cix-fra", site=cls.site)
        cls.prefix = Prefix.objects.create(prefix="80.81.192.0/22")
        cls.peering_network = PeeringNetwork.objects.create(fabric=cls.fabric, name="Production LAN", prefix=cls.prefix)

        # Create BGP sessions
        cls.session1 = BGPSession.objects.create(
            name="peer-as65001",
            device=cls.device1,
            site=cls.site,
            local_as=cls.local_as,
            remote_as=cls.remote_as1,
            local_address=cls.local_ip1,
            remote_address=cls.remote_ip1,
            status="active",
            enabled=True,
            peer_group=cls.peer_group1,
            relationship=cls.relationship,
            bfd=cls.bfd_profile,
            peering_network=cls.peering_network,
            password="secret123",
            multihop_ttl=2,
            description="Session to AS65001",
        )
        cls.session1.import_policies.add(cls.import_policy, cls.common_policy)
        cls.session1.export_policies.add(cls.export_policy)

        cls.session2 = BGPSession.objects.create(
            name="peer-as65002",
            device=cls.device1,
            site=cls.site,
            local_as=cls.local_as,
            remote_as=cls.remote_as2,
            local_address=cls.local_ip2,
            remote_address=cls.remote_ip2,
            status="active",
            enabled=True,
            peer_group=cls.peer_group1,  # Same peer group as session1
            description="Session to AS65002",
        )
        cls.session2.import_policies.add(cls.import_policy)
        cls.session2.export_policies.add(cls.export_policy, cls.common_policy)

        # IPv6 session on device2
        cls.session3 = BGPSession.objects.create(
            name="peer-ipv6",
            device=cls.device2,
            site=cls.site,
            local_as=cls.local_as,
            remote_as=cls.remote_as1,
            local_address=cls.local_ip3,
            remote_address=cls.remote_ip3,
            status="active",
            enabled=True,
            peer_group=cls.peer_group2,
        )

    def test_build_context_with_device_returns_all_sessions(self):
        """Test that build_context with device returns all sessions for that device."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        # Should return both sessions for device1
        self.assertEqual(len(context["sessions"]), 2)
        session_names = {s["name"] for s in context["sessions"]}
        self.assertIn("peer-as65001", session_names)
        self.assertIn("peer-as65002", session_names)

    def test_build_context_with_specific_sessions(self):
        """Test that build_context with specific sessions uses those sessions."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        # Should return only the specified session
        self.assertEqual(len(context["sessions"]), 1)
        self.assertEqual(context["sessions"][0]["name"], "peer-as65001")

    def test_build_context_session_includes_policies(self):
        """Test that session context includes import and export policies."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]

        # Check import policies
        self.assertEqual(len(session["import_policies"]), 2)
        import_policy_names = {p["name"] for p in session["import_policies"]}
        self.assertIn("IMPORT-PEER", import_policy_names)
        self.assertIn("COMMON-POLICY", import_policy_names)

        # Check export policies
        self.assertEqual(len(session["export_policies"]), 1)
        self.assertEqual(session["export_policies"][0]["name"], "EXPORT-PEER")

    def test_build_context_includes_deduplicated_peer_groups(self):
        """Test that context includes deduplicated peer groups from sessions."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        # Both sessions use peer_group1, should only appear once
        self.assertEqual(len(context["peer_groups"]), 1)
        self.assertEqual(context["peer_groups"][0]["name"], "PEERS")
        self.assertEqual(context["peer_groups"][0]["id"], self.peer_group1.pk)

    def test_build_context_includes_deduplicated_routing_policies(self):
        """Test that context includes deduplicated routing policies from sessions."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        # Should have 3 unique policies (import, export, common)
        self.assertEqual(len(context["routing_policies"]), 3)
        policy_names = {p["name"] for p in context["routing_policies"]}
        self.assertIn("IMPORT-PEER", policy_names)
        self.assertIn("EXPORT-PEER", policy_names)
        self.assertIn("COMMON-POLICY", policy_names)

    def test_build_context_empty_device_returns_empty_sessions(self):
        """Test that device with no sessions returns empty sessions list."""
        # Create a device with no sessions
        empty_device = Device.objects.create(
            name="empty-router",
            site=self.site,
            role=self.device_role,
            device_type=self.device_type,
        )

        renderer = ConfigRenderer()
        context = renderer.build_context(device=empty_device)

        self.assertEqual(context["sessions"], [])
        self.assertEqual(context["peer_groups"], [])
        self.assertEqual(context["routing_policies"], [])
        self.assertEqual(context["prefix_lists"], [])
        self.assertEqual(context["communities"], [])

    def test_build_context_no_args_returns_empty(self):
        """Test that build_context with no arguments returns empty context."""
        renderer = ConfigRenderer()
        context = renderer.build_context()

        self.assertIsNone(context["device"])
        self.assertEqual(context["sessions"], [])
        self.assertEqual(context["peer_groups"], [])
        self.assertEqual(context["routing_policies"], [])

    def test_session_serialization_includes_all_fields(self):
        """Test that session serialization includes all required fields."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]

        # Check all required fields are present
        self.assertEqual(session["id"], self.session1.pk)
        self.assertEqual(session["name"], "peer-as65001")
        self.assertEqual(session["description"], "Session to AS65001")
        self.assertEqual(session["status"], "active")
        self.assertTrue(session["enabled"])
        self.assertEqual(session["local_asn"], 65000)
        self.assertEqual(session["peer_asn"], 65001)
        self.assertEqual(session["local_ip"], "192.0.2.1")
        self.assertEqual(session["remote_ip"], "192.0.2.2")
        self.assertEqual(session["relationship"], "Peer")
        self.assertEqual(session["password"], "secret123")
        self.assertEqual(session["multihop_ttl"], 2)

    def test_session_serialization_includes_bfd_profile(self):
        """Test that session with BFD profile includes BFD details."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        bfd = session["bfd_profile"]

        self.assertIsNotNone(bfd)
        self.assertEqual(bfd["name"], "fast-bfd")
        self.assertEqual(bfd["minimum_interval"], 100)
        self.assertEqual(bfd["multiplier"], 3)

    def test_session_serialization_includes_peer_group(self):
        """Test that session with peer group includes peer group details."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        peer_group = session["peer_group"]

        self.assertIsNotNone(peer_group)
        self.assertEqual(peer_group["id"], self.peer_group1.pk)
        self.assertEqual(peer_group["name"], "PEERS")
        self.assertEqual(peer_group["description"], "Peer sessions")

    def test_session_serialization_includes_peering_network(self):
        """Test that session with peering network includes network details."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        network = session["peering_network"]

        self.assertIsNotNone(network)
        self.assertEqual(network["id"], self.peering_network.pk)
        self.assertEqual(network["name"], "Production LAN")
        self.assertEqual(network["fabric"], "DE-CIX Frankfurt")

    def test_device_serialization_includes_platform(self):
        """Test that device serialization includes platform details."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        device = context["device"]
        self.assertIsNotNone(device)
        self.assertEqual(device["name"], "router1")
        self.assertIsNotNone(device["platform"])
        self.assertEqual(device["platform"]["name"], "Junos")
        self.assertEqual(device["platform"]["slug"], "junos")

    def test_device_serialization_includes_site(self):
        """Test that device serialization includes site details."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        device = context["device"]
        self.assertIsNotNone(device["site"])
        self.assertEqual(device["site"]["name"], "Test Site")
        self.assertEqual(device["site"]["slug"], "test-site")

    def test_afi_safis_derived_from_ipv4_address(self):
        """Test that afi_safis is derived correctly for IPv4 sessions."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        self.assertIn("ipv4-unicast", session["afi_safis"])
        self.assertNotIn("ipv6-unicast", session["afi_safis"])

    def test_afi_safis_derived_from_ipv6_address(self):
        """Test that afi_safis is derived correctly for IPv6 sessions."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session3])

        session = context["sessions"][0]
        self.assertIn("ipv6-unicast", session["afi_safis"])
        self.assertNotIn("ipv4-unicast", session["afi_safis"])

    def test_policy_serialization_includes_weight_and_family(self):
        """Test that policy serialization includes weight and address_family."""
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        # Find the IMPORT-PEER policy
        import_peer = next((p for p in session["import_policies"] if p["name"] == "IMPORT-PEER"), None)

        self.assertIsNotNone(import_peer)
        self.assertEqual(import_peer["weight"], 100)
        self.assertIn("address_family", import_peer)

    def test_session_without_optional_fields(self):
        """Test serialization of session without optional fields (BFD, peer_group, etc)."""
        # session3 has no BFD, relationship, password, peering_network
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session3])

        session = context["sessions"][0]

        self.assertIsNone(session["bfd_profile"])
        self.assertIsNone(session["relationship"])
        self.assertEqual(session["password"], "")
        self.assertIsNone(session["peering_network"])
        # But should have peer_group
        self.assertIsNotNone(session["peer_group"])

    def test_multiple_peer_groups_from_multiple_devices(self):
        """Test that multiple peer groups are extracted from sessions across devices."""
        renderer = ConfigRenderer()
        # Get sessions from both devices
        context = renderer.build_context(sessions=[self.session1, self.session3])

        # Should have 2 different peer groups
        self.assertEqual(len(context["peer_groups"]), 2)
        peer_group_names = {pg["name"] for pg in context["peer_groups"]}
        self.assertIn("PEERS", peer_group_names)
        self.assertIn("TRANSIT", peer_group_names)

    def test_context_structure_keys(self):
        """Test that context has all required top-level keys."""
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1)

        expected_keys = {
            "device",
            "sessions",
            "peer_groups",
            "routing_policies",
            "prefix_lists",
            "communities",
        }
        self.assertEqual(set(context.keys()), expected_keys)
