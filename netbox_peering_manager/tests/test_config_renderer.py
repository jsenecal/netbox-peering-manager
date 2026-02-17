"""Tests for ConfigRenderer service."""

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Site
from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress, Prefix
from netbox_routing.models import BGPPeer

from netbox_peering_manager.models import (
    PeerASN,
    PeeringFabric,
    PeeringNetwork,
    PeeringSession,
    Relationship,
)
from netbox_peering_manager.services.config_renderer import ConfigRenderer


class ConfigRendererTestCase(TestCase):
    """Test cases for ConfigRenderer.build_context()."""

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name="Test Site", slug="test-site")
        cls.platform = Platform.objects.create(name="Junos", slug="junos")

        cls.manufacturer = Manufacturer.objects.create(name="Juniper", slug="juniper")
        cls.device_type = DeviceType.objects.create(manufacturer=cls.manufacturer, model="MX480", slug="mx480")
        cls.device_role = DeviceRole.objects.create(name="Router", slug="router")

        cls.device1 = Device.objects.create(
            name="router1",
            site=cls.site,
            role=cls.device_role,
            device_type=cls.device_type,
            platform=cls.platform,
        )

        cls.rir = RIR.objects.create(name="Test RIR", slug="test-rir")
        cls.local_as = ASN.objects.create(asn=65000, rir=cls.rir)
        remote_asn1 = ASN.objects.create(asn=65001, rir=cls.rir)
        remote_asn2 = ASN.objects.create(asn=65002, rir=cls.rir)
        cls.remote_as1 = PeerASN.objects.create(asn=remote_asn1, irr_as_set="AS-TEST1")
        cls.remote_as2 = PeerASN.objects.create(asn=remote_asn2, irr_as_set="AS-TEST2")

        cls.local_ip1 = IPAddress.objects.create(address="192.0.2.1/32")
        cls.remote_ip1 = IPAddress.objects.create(address="192.0.2.2/32")
        cls.local_ip2 = IPAddress.objects.create(address="192.0.2.3/32")
        cls.remote_ip2 = IPAddress.objects.create(address="192.0.2.4/32")
        cls.local_ip3 = IPAddress.objects.create(address="2001:db8::1/128")
        cls.remote_ip3 = IPAddress.objects.create(address="2001:db8::2/128")

        cls.relationship = Relationship.objects.create(name="Peer", slug="peer")

        cls.fabric = PeeringFabric.objects.create(name="DE-CIX Frankfurt", slug="de-cix-fra", site=cls.site)
        cls.prefix = Prefix.objects.create(prefix="80.81.192.0/22")
        cls.peering_network = PeeringNetwork.objects.create(fabric=cls.fabric, name="Production LAN", prefix=cls.prefix)

        # Create BGPPeer objects (from netbox-routing)
        cls.bgp_peer1 = BGPPeer.objects.create(
            name="peer-as65001",
            peer=cls.remote_ip1,
            source=cls.local_ip1,
            remote_as=remote_asn1,
            local_as=cls.local_as,
            password="secret123",
            ttl=2,
        )

        cls.bgp_peer2 = BGPPeer.objects.create(
            name="peer-as65002",
            peer=cls.remote_ip2,
            source=cls.local_ip2,
            remote_as=remote_asn2,
            local_as=cls.local_as,
        )

        cls.bgp_peer3 = BGPPeer.objects.create(
            name="peer-ipv6",
            peer=cls.remote_ip3,
            source=cls.local_ip3,
            remote_as=remote_asn1,
            local_as=cls.local_as,
        )

        # Create PeeringSession extension objects
        cls.session1 = PeeringSession.objects.create(
            bgp_peer=cls.bgp_peer1,
            relationship=cls.relationship,
            peering_network=cls.peering_network,
            service_reference="SVC-001",
        )

        cls.session2 = PeeringSession.objects.create(
            bgp_peer=cls.bgp_peer2,
        )

        cls.session3 = PeeringSession.objects.create(
            bgp_peer=cls.bgp_peer3,
        )

    def test_build_context_with_specific_sessions(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        self.assertEqual(len(context["sessions"]), 1)
        self.assertEqual(context["sessions"][0]["name"], "peer-as65001")

    def test_build_context_no_args_returns_empty(self):
        renderer = ConfigRenderer()
        context = renderer.build_context()

        self.assertIsNone(context["device"])
        self.assertEqual(context["sessions"], [])
        self.assertEqual(context["peer_groups"], [])
        self.assertEqual(context["route_maps"], [])

    def test_session_serialization_includes_all_fields(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]

        self.assertEqual(session["id"], self.session1.pk)
        self.assertEqual(session["name"], "peer-as65001")
        self.assertEqual(session["local_asn"], 65000)
        self.assertEqual(session["peer_asn"], 65001)
        self.assertEqual(session["local_ip"], "192.0.2.1")
        self.assertEqual(session["remote_ip"], "192.0.2.2")
        self.assertEqual(session["relationship"], "Peer")
        self.assertEqual(session["service_reference"], "SVC-001")
        self.assertEqual(session["password"], "secret123")
        self.assertEqual(session["ttl"], 2)

    def test_session_serialization_includes_peering_network(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        network = session["peering_network"]

        self.assertIsNotNone(network)
        self.assertEqual(network["id"], self.peering_network.pk)
        self.assertEqual(network["name"], "Production LAN")
        self.assertEqual(network["fabric"], "DE-CIX Frankfurt")

    def test_session_serialization_includes_peer_asn_info(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        self.assertEqual(session["irr_as_set"], "AS-TEST1")

    def test_device_serialization_includes_platform(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1, sessions=[])

        device = context["device"]
        self.assertIsNotNone(device)
        self.assertEqual(device["name"], "router1")
        self.assertIsNotNone(device["platform"])
        self.assertEqual(device["platform"]["name"], "Junos")
        self.assertEqual(device["platform"]["slug"], "junos")

    def test_device_serialization_includes_site(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device1, sessions=[])

        device = context["device"]
        self.assertIsNotNone(device["site"])
        self.assertEqual(device["site"]["name"], "Test Site")
        self.assertEqual(device["site"]["slug"], "test-site")

    def test_afi_safis_derived_from_ipv4_address(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        session = context["sessions"][0]
        self.assertIn("ipv4-unicast", session["afi_safis"])
        self.assertNotIn("ipv6-unicast", session["afi_safis"])

    def test_afi_safis_derived_from_ipv6_address(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session3])

        session = context["sessions"][0]
        self.assertIn("ipv6-unicast", session["afi_safis"])
        self.assertNotIn("ipv4-unicast", session["afi_safis"])

    def test_session_without_optional_fields(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session3])

        session = context["sessions"][0]

        self.assertIsNone(session["bfd_profile"])
        self.assertIsNone(session["relationship"])
        self.assertEqual(session["password"], "")
        self.assertIsNone(session["peering_network"])

    def test_context_structure_keys(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session1])

        expected_keys = {
            "device",
            "sessions",
            "peer_groups",
            "route_maps",
            "prefix_lists",
            "communities",
        }
        self.assertEqual(set(context.keys()), expected_keys)
