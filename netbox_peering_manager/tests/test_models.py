from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress, Prefix
from tenancy.models import Tenant

from netbox_peering_manager.models import (
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    RoutingPolicy,
)


class RoutingPolicyTestCase(TestCase):
    def setUp(self):
        rp_name = "test_policy"
        self.rp = RoutingPolicy.objects.create(name=rp_name, description=rp_name)

    def test_create_routing_policy(self):
        self.assertTrue(isinstance(self.rp, RoutingPolicy))
        self.assertEqual(self.rp.__str__(), self.rp.name)

    def test_unique_together(self):
        rp = RoutingPolicy(name=self.rp.name, description=self.rp.description)
        with self.assertRaises(IntegrityError):
            rp.save()


class BGPPeerGroupTestCase(TestCase):
    def setUp(self):
        self.in_policy1 = RoutingPolicy.objects.create(name="in_policy_1")
        self.in_policy2 = RoutingPolicy.objects.create(name="in_policy_2")
        self.out_policy1 = RoutingPolicy.objects.create(name="out_policy_1")
        self.out_policy2 = RoutingPolicy.objects.create(name="out_policy_2")
        self.peer_group = BGPPeerGroup.objects.create(name="peer_group", description="peer_group")

    def test_create_peer_group(self):
        self.assertTrue(isinstance(self.peer_group, BGPPeerGroup))
        self.assertEqual(self.peer_group.__str__(), self.peer_group.name)

    def test_peer_group_polciy_realtions(self):
        peer_group = BGPPeerGroup.objects.create(
            name="group1",
        )
        peer_group.import_policies.add(self.in_policy1)
        peer_group.import_policies.add(self.in_policy2)
        peer_group.export_policies.add(self.out_policy1)
        peer_group.export_policies.add(self.out_policy2)
        self.assertEqual(peer_group.import_policies.get(pk=self.in_policy1.pk), self.in_policy1)
        self.assertEqual(peer_group.import_policies.get(pk=self.in_policy2.pk), self.in_policy2)
        self.assertEqual(peer_group.export_policies.get(pk=self.out_policy1.pk), self.out_policy1)
        self.assertEqual(peer_group.export_policies.get(pk=self.out_policy2.pk), self.out_policy2)

    def test_unique_together(self):
        peer_group = BGPPeerGroup(name="peer_group", description="peer_group")
        with self.assertRaises(IntegrityError):
            peer_group.save()

    def test_ununique_together(self):
        peer_group1 = BGPPeerGroup(name="peer_group1", description="peer_group")
        peer_group1.save()


class CommunityTestCase(TestCase):
    def setUp(self):
        self.community = Community.objects.create(value="65001:65001", description="test_community")

    def test_create_community(self):
        self.assertTrue(isinstance(self.community, Community))
        self.assertEqual(self.community.__str__(), self.community.value)

    def test_invalid_community(self):
        community = Community(value=0)
        self.assertRaises(ValidationError, community.full_clean)


class CommunityListTestCase(TestCase):
    def setUp(self):
        self.communitylist = CommunityList.objects.create(
            name="community_list_1", description="test_community_list", comments="comment_cl1"
        )

    def test_create_community(self):
        self.assertTrue(isinstance(self.communitylist, CommunityList))
        self.assertEqual(self.communitylist.__str__(), self.communitylist.name)

    def test_unique_together(self):
        communitylist2 = CommunityList(
            name="community_list_1",
            description="test_community_list",
        )
        with self.assertRaises(IntegrityError):
            communitylist2.save()


class BGPSessionTestCase(TestCase):
    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="device type")
        device_role = DeviceRole.objects.create(name="device role")
        self.site = Site.objects.create(name="site")
        self.tenant = Tenant.objects.create(name="tenant")
        self.device = Device.objects.create(name="device", site=self.site, role=device_role, device_type=device_type)
        self.rir = RIR.objects.create(name="rir")
        self.local_as = ASN.objects.create(asn=65001, rir=self.rir)
        self.remote_as = ASN.objects.create(asn=65002, rir=self.rir)
        self.peer_group = BGPPeerGroup.objects.create(name="peer_group")
        self.routing_policy_in = RoutingPolicy.objects.create(name="policy_in")
        self.routing_policy_out = RoutingPolicy.objects.create(name="policy_out")
        self.local_ip = IPAddress.objects.create(address="1.1.1.1/32")
        self.remote_ip = IPAddress.objects.create(address="1.1.1.2/32")
        self.session = BGPSession.objects.create(
            name="session",
            site=self.site,
            tenant=self.tenant,
            device=self.device,
            local_address=self.local_ip,
            remote_address=self.remote_ip,
            local_as=self.local_as,
            remote_as=self.remote_as,
            status="active",
            peer_group=self.peer_group,
        )

    def test_create_session(self):
        self.assertTrue(isinstance(self.session, BGPSession))
        self.assertEqual(self.session.__str__(), f"{self.session.device}:{self.session.name}")

    def test_policies(self):
        pass

    def test_unique_together(self):
        pass


class PeeringFabricTypeTestCase(TestCase):
    def setUp(self):
        self.fabric_type = PeeringFabricType.objects.create(
            name="Internet Exchange",
            slug="internet-exchange",
            description="Public Internet Exchange Point",
        )

    def test_create_fabric_type(self):
        self.assertTrue(isinstance(self.fabric_type, PeeringFabricType))
        self.assertEqual(self.fabric_type.__str__(), self.fabric_type.name)

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            PeeringFabricType.objects.create(
                name="Internet Exchange",
                slug="internet-exchange-2",
            )

    def test_unique_slug(self):
        with self.assertRaises(IntegrityError):
            PeeringFabricType.objects.create(
                name="Internet Exchange 2",
                slug="internet-exchange",
            )

    def test_get_absolute_url(self):
        url = self.fabric_type.get_absolute_url()
        self.assertIn(str(self.fabric_type.pk), url)


class PeeringFabricTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.tenant = Tenant.objects.create(name="Test Tenant", slug="test-tenant")
        self.fabric_type = PeeringFabricType.objects.create(
            name="Internet Exchange",
            slug="internet-exchange",
        )
        self.fabric = PeeringFabric.objects.create(
            name="AMS-IX",
            slug="ams-ix",
            description="Amsterdam Internet Exchange",
            type=self.fabric_type,
            site=self.site,
            tenant=self.tenant,
            peeringdb_id=26,
        )

    def test_create_fabric(self):
        self.assertTrue(isinstance(self.fabric, PeeringFabric))
        self.assertEqual(self.fabric.__str__(), self.fabric.name)

    def test_fabric_with_type(self):
        self.assertEqual(self.fabric.type, self.fabric_type)

    def test_fabric_with_site(self):
        self.assertEqual(self.fabric.site, self.site)

    def test_fabric_with_tenant(self):
        self.assertEqual(self.fabric.tenant, self.tenant)

    def test_unique_together_name_site(self):
        with self.assertRaises(IntegrityError):
            PeeringFabric.objects.create(
                name="AMS-IX",
                slug="ams-ix-2",
                site=self.site,
            )

    def test_get_status_color(self):
        color = self.fabric.get_status_color()
        self.assertIsNotNone(color)

    def test_get_absolute_url(self):
        url = self.fabric.get_absolute_url()
        self.assertIn(str(self.fabric.pk), url)


class PeeringNetworkTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", slug="test-site")
        self.fabric = PeeringFabric.objects.create(
            name="AMS-IX",
            slug="ams-ix",
            site=self.site,
        )
        self.prefix = Prefix.objects.create(prefix="80.249.208.0/21")
        self.network = PeeringNetwork.objects.create(
            fabric=self.fabric,
            name="Production Peering LAN",
            prefix=self.prefix,
            description="Main peering LAN",
        )

    def test_create_network(self):
        self.assertTrue(isinstance(self.network, PeeringNetwork))
        self.assertEqual(self.network.__str__(), f"{self.fabric.name}: {self.network.name}")

    def test_network_belongs_to_fabric(self):
        self.assertEqual(self.network.fabric, self.fabric)

    def test_network_has_prefix(self):
        self.assertEqual(self.network.prefix, self.prefix)

    def test_unique_together_fabric_name(self):
        with self.assertRaises(IntegrityError):
            PeeringNetwork.objects.create(
                fabric=self.fabric,
                name="Production Peering LAN",
                prefix=self.prefix,
            )

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
            name="router1",
            site=self.site,
            role=self.device_role,
            device_type=self.device_type,
        )
        self.interface = Interface.objects.create(
            device=self.device,
            name="eth0",
            type="1000base-t",
        )
        self.fabric = PeeringFabric.objects.create(
            name="AMS-IX",
            slug="ams-ix",
            site=self.site,
        )
        self.prefix = Prefix.objects.create(prefix="80.249.208.0/21")
        self.network = PeeringNetwork.objects.create(
            fabric=self.fabric,
            name="Production Peering LAN",
            prefix=self.prefix,
        )
        self.connection = PeeringConnection.objects.create(
            peering_network=self.network,
            interface=self.interface,
            description="Primary connection",
        )

    def test_create_connection(self):
        self.assertTrue(isinstance(self.connection, PeeringConnection))
        self.assertEqual(self.connection.__str__(), f"{self.network}: {self.interface}")

    def test_connection_belongs_to_network(self):
        self.assertEqual(self.connection.peering_network, self.network)

    def test_connection_has_interface(self):
        self.assertEqual(self.connection.interface, self.interface)

    def test_device_property(self):
        self.assertEqual(self.connection.device, self.device)

    def test_unique_together_network_interface(self):
        with self.assertRaises(IntegrityError):
            PeeringConnection.objects.create(
                peering_network=self.network,
                interface=self.interface,
            )

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
