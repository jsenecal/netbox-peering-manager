from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress, Prefix
from netbox_routing.models import BGPPeer, PrefixList
from tenancy.models import Tenant

from netbox_peering_manager.models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PeeringSession,
    Relationship,
)


class IRRSourceTestCase(TestCase):
    def setUp(self):
        self.irr_source = IRRSource.objects.create(
            name="Test IRR",
            slug="test-irr",
            url="http://irr.example.com/",
        )

    def test_create_irr_source(self):
        self.assertTrue(isinstance(self.irr_source, IRRSource))
        self.assertEqual(str(self.irr_source), self.irr_source.name)

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            IRRSource.objects.create(name="Test IRR", slug="test-irr-2", url="http://irr2.example.com/")

    def test_get_absolute_url(self):
        url = self.irr_source.get_absolute_url()
        self.assertIn(str(self.irr_source.pk), url)

    def test_sync_interval_rejects_zero(self):
        """sync_interval=0 should fail validation (MinValueValidator(1))."""
        irr = IRRSource(
            name="Zero Interval IRR",
            slug="zero-interval-irr",
            url="http://irr.example.com/",
            sync_interval=0,
        )
        with self.assertRaises(ValidationError) as ctx:
            irr.full_clean()
        self.assertIn("sync_interval", ctx.exception.message_dict)

    def test_sync_interval_accepts_one(self):
        """sync_interval=1 should pass validation."""
        irr = IRRSource(
            name="One Minute IRR",
            slug="one-minute-irr",
            url="http://irr.example.com/",
            sync_interval=1,
        )
        irr.full_clean()  # Should not raise


class RelationshipTestCase(TestCase):
    def setUp(self):
        self.relationship = Relationship.objects.create(name="Transit", slug="transit")

    def test_create_relationship(self):
        self.assertTrue(isinstance(self.relationship, Relationship))
        self.assertEqual(str(self.relationship), self.relationship.name)

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Relationship.objects.create(name="Transit", slug="transit-2")


class PeerASNTestCase(TestCase):
    def setUp(self):
        self.rir = RIR.objects.create(name="Test RIR")
        self.asn = ASN.objects.create(asn=65001, rir=self.rir)
        self.peer_asn = PeerASN.objects.create(asn=self.asn)

    def test_create_peer_asn(self):
        self.assertTrue(isinstance(self.peer_asn, PeerASN))
        self.assertEqual(str(self.peer_asn), "AS65001")

    def test_asn_number_property(self):
        self.assertEqual(self.peer_asn.asn_number, 65001)

    def test_unique_asn(self):
        with self.assertRaises(IntegrityError):
            PeerASN.objects.create(asn=self.asn)


class IRRPrefixListConfigTestCase(TestCase):
    def setUp(self):
        self.irr_source = IRRSource.objects.create(name="Test IRR", slug="test-irr", url="http://irr.example.com/")
        self.prefix_list = PrefixList.objects.create(name="Test PL", family=4)
        self.config = IRRPrefixListConfig.objects.create(
            prefix_list=self.prefix_list,
            irr_source=self.irr_source,
            source_as_set="AS-TEST",
        )

    def test_create_config(self):
        self.assertTrue(isinstance(self.config, IRRPrefixListConfig))
        self.assertIn("Test PL", str(self.config))

    def test_is_irr_managed(self):
        self.assertTrue(self.config.is_irr_managed)

    def test_not_irr_managed_without_source(self):
        config = IRRPrefixListConfig(prefix_list=self.prefix_list)
        self.assertFalse(config.is_irr_managed)

    def test_validation_source_without_as_set(self):
        config = IRRPrefixListConfig(
            prefix_list=self.prefix_list,
            irr_source=self.irr_source,
            source_as_set="",
        )
        with self.assertRaises(ValidationError):
            config.full_clean()

    def test_validation_as_set_without_source(self):
        pl2 = PrefixList.objects.create(name="Test PL 2", family=4)
        config = IRRPrefixListConfig(
            prefix_list=pl2,
            source_as_set="AS-TEST",
        )
        with self.assertRaises(ValidationError):
            config.full_clean()

    def test_get_absolute_url(self):
        url = self.config.get_absolute_url()
        self.assertIn(str(self.config.pk), url)

    def test_sync_interval_rejects_zero(self):
        """sync_interval=0 should fail validation (MinValueValidator(1))."""
        pl = PrefixList.objects.create(name="Zero Interval PL", family=4)
        config = IRRPrefixListConfig(
            prefix_list=pl,
            sync_interval=0,
        )
        with self.assertRaises(ValidationError) as ctx:
            config.full_clean()
        self.assertIn("sync_interval", ctx.exception.message_dict)

    def test_sync_interval_accepts_one(self):
        """sync_interval=1 should pass validation."""
        pl = PrefixList.objects.create(name="One Min PL", family=4)
        config = IRRPrefixListConfig(
            prefix_list=pl,
            sync_interval=1,
        )
        config.full_clean()  # Should not raise


class PeeringSessionTestCase(TestCase):
    def setUp(self):
        self.rir = RIR.objects.create(name="Test RIR")
        remote_asn = ASN.objects.create(asn=65001, rir=self.rir)
        remote_ip = IPAddress.objects.create(address="192.0.2.1/32")
        self.bgp_peer = BGPPeer.objects.create(
            name="test-peer",
            peer=remote_ip,
            remote_as=remote_asn,
        )
        self.relationship = Relationship.objects.create(name="Peer", slug="peer")
        self.session = PeeringSession.objects.create(
            bgp_peer=self.bgp_peer,
            relationship=self.relationship,
            service_reference="TICKET-123",
        )

    def test_create_session(self):
        self.assertTrue(isinstance(self.session, PeeringSession))
        self.assertIn("test-peer", str(self.session))

    def test_session_has_relationship(self):
        self.assertEqual(self.session.relationship, self.relationship)

    def test_session_unique_bgp_peer(self):
        with self.assertRaises(IntegrityError):
            PeeringSession.objects.create(bgp_peer=self.bgp_peer)

    def test_bgp_peer_protect_on_delete(self):
        """Deleting a BGPPeer with a PeeringSession should raise ProtectedError."""
        with self.assertRaises(models.ProtectedError):
            self.bgp_peer.delete()

    def test_bgp_peer_deletable_after_session_removed(self):
        """Deleting a BGPPeer should succeed once the PeeringSession is removed."""
        self.session.delete()
        self.bgp_peer.delete()
        self.assertFalse(BGPPeer.objects.filter(pk=self.bgp_peer.pk).exists())

    def test_get_absolute_url(self):
        url = self.session.get_absolute_url()
        self.assertIn(str(self.session.pk), url)


class PeeringFabricTypeTestCase(TestCase):
    def setUp(self):
        self.fabric_type = PeeringFabricType.objects.create(
            name="Internet Exchange",
            slug="internet-exchange",
            description="Public Internet Exchange Point",
        )

    def test_create_fabric_type(self):
        self.assertTrue(isinstance(self.fabric_type, PeeringFabricType))
        self.assertEqual(str(self.fabric_type), self.fabric_type.name)

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            PeeringFabricType.objects.create(name="Internet Exchange", slug="internet-exchange-2")

    def test_unique_slug(self):
        with self.assertRaises(IntegrityError):
            PeeringFabricType.objects.create(name="Internet Exchange 2", slug="internet-exchange")

    def test_get_absolute_url(self):
        url = self.fabric_type.get_absolute_url()
        self.assertIn(str(self.fabric_type.pk), url)


class PeeringFabricTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.tenant = Tenant.objects.create(name="Test Tenant", slug="test-tenant")
        self.fabric_type = PeeringFabricType.objects.create(name="Internet Exchange", slug="internet-exchange")
        self.fabric = PeeringFabric.objects.create(
            name="AMS-IX",
            slug="ams-ix",
            description="Amsterdam Internet Exchange",
            type=self.fabric_type,
            site=self.site,
            tenant=self.tenant,
        )

    def test_create_fabric(self):
        self.assertTrue(isinstance(self.fabric, PeeringFabric))
        self.assertEqual(str(self.fabric), self.fabric.name)

    def test_fabric_with_type(self):
        self.assertEqual(self.fabric.type, self.fabric_type)

    def test_fabric_with_site(self):
        self.assertEqual(self.fabric.site, self.site)

    def test_fabric_with_tenant(self):
        self.assertEqual(self.fabric.tenant, self.tenant)

    def test_unique_together_name_site(self):
        with self.assertRaises(IntegrityError):
            PeeringFabric.objects.create(name="AMS-IX", slug="ams-ix-2", site=self.site)

    def test_get_status_color(self):
        color = self.fabric.get_status_color()
        self.assertIsNotNone(color)

    def test_get_absolute_url(self):
        url = self.fabric.get_absolute_url()
        self.assertIn(str(self.fabric.pk), url)


class PeeringNetworkTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.fabric = PeeringFabric.objects.create(name="AMS-IX", slug="ams-ix", site=self.site)
        self.prefix = Prefix.objects.create(prefix="80.249.208.0/21")
        self.network = PeeringNetwork.objects.create(
            fabric=self.fabric,
            name="Production Peering LAN",
            prefix=self.prefix,
            description="Main peering LAN",
        )

    def test_create_network(self):
        self.assertTrue(isinstance(self.network, PeeringNetwork))
        self.assertEqual(str(self.network), f"{self.fabric.name}: {self.network.name}")

    def test_network_belongs_to_fabric(self):
        self.assertEqual(self.network.fabric, self.fabric)

    def test_network_has_prefix(self):
        self.assertEqual(self.network.prefix, self.prefix)

    def test_unique_together_fabric_name(self):
        with self.assertRaises(IntegrityError):
            PeeringNetwork.objects.create(fabric=self.fabric, name="Production Peering LAN", prefix=self.prefix)

    def test_cascade_delete_fabric(self):
        network_pk = self.network.pk
        self.fabric.delete()
        self.assertFalse(PeeringNetwork.objects.filter(pk=network_pk).exists())

    def test_get_status_color(self):
        color = self.network.get_status_color()
        self.assertIsNotNone(color)

    def test_get_absolute_url(self):
        url = self.network.get_absolute_url()
        self.assertIn(str(self.network.pk), url)


class PeeringConnectionTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        self.device_type = DeviceType.objects.create(manufacturer=self.manufacturer, model="Test Model")
        self.device_role = DeviceRole.objects.create(name="Router", slug="router")
        self.device = Device.objects.create(
            name="router1", site=self.site, role=self.device_role, device_type=self.device_type
        )
        self.interface = Interface.objects.create(device=self.device, name="eth0", type="1000base-t")
        self.fabric = PeeringFabric.objects.create(name="AMS-IX", slug="ams-ix", site=self.site)
        self.prefix = Prefix.objects.create(prefix="80.249.208.0/21")
        self.network = PeeringNetwork.objects.create(
            fabric=self.fabric, name="Production Peering LAN", prefix=self.prefix
        )
        self.connection = PeeringConnection.objects.create(
            peering_network=self.network, interface=self.interface, description="Primary connection"
        )

    def test_create_connection(self):
        self.assertTrue(isinstance(self.connection, PeeringConnection))
        self.assertEqual(str(self.connection), f"{self.network}: {self.interface}")

    def test_connection_belongs_to_network(self):
        self.assertEqual(self.connection.peering_network, self.network)

    def test_connection_has_interface(self):
        self.assertEqual(self.connection.interface, self.interface)

    def test_device_property(self):
        self.assertEqual(self.connection.device, self.device)

    def test_unique_together_network_interface(self):
        with self.assertRaises(IntegrityError):
            PeeringConnection.objects.create(peering_network=self.network, interface=self.interface)

    def test_cascade_delete_network(self):
        connection_pk = self.connection.pk
        self.network.delete()
        self.assertFalse(PeeringConnection.objects.filter(pk=connection_pk).exists())

    def test_get_status_color(self):
        color = self.connection.get_status_color()
        self.assertIsNotNone(color)

    def test_get_absolute_url(self):
        url = self.connection.get_absolute_url()
        self.assertIn(str(self.connection.pk), url)
