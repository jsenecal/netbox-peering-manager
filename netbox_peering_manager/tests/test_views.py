"""View tests for netbox_peering_manager plugin."""

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import ASN, RIR, IPAddress, Prefix
from netbox_routing.models import BGPPeer, PrefixList
from utilities.testing import ViewTestCases, create_tags

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


class PluginURLMixin:
    """Mixin to fix URL namespace for plugin view tests."""

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"


class RelationshipTestCase(PluginURLMixin, ViewTestCases.OrganizationalObjectViewTestCase):
    model = Relationship

    @classmethod
    def setUpTestData(cls):
        relationships = (
            Relationship(name="Transit", slug="transit", color="ff0000"),
            Relationship(name="Peer", slug="peer", color="00ff00"),
            Relationship(name="Customer", slug="customer", color="0000ff"),
        )
        Relationship.objects.bulk_create(relationships)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "IXP",
            "slug": "ixp",
            "color": "ffff00",
            "description": "Internet Exchange Point",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,color",
            "Transit Provider,transit-provider,aabbcc",
            "Private Peer,private-peer,ddeeff",
            "Route Server,route-server,112233",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{relationships[0].pk},Transit Updated,Updated description",
            f"{relationships[1].pk},Peer Updated,Updated description",
            f"{relationships[2].pk},Customer Updated,Updated description",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated description",
        }


class IRRSourceTestCase(PluginURLMixin, ViewTestCases.OrganizationalObjectViewTestCase):
    model = IRRSource

    @classmethod
    def setUpTestData(cls):
        irr_sources = (
            IRRSource(name="Primary IRR", slug="primary-irr", url="http://irr1.example.com/"),
            IRRSource(name="Secondary IRR", slug="secondary-irr", url="http://irr2.example.com/"),
            IRRSource(name="Tertiary IRR", slug="tertiary-irr", url="http://irr3.example.com/"),
        )
        IRRSource.objects.bulk_create(irr_sources)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New IRR",
            "slug": "new-irr",
            "url": "http://new-irr.example.com/",
            "enabled": True,
            "sync_interval": 1440,
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,url,sync_interval",
            "IRR Source 4,irr-source-4,http://irr4.example.com/,1440",
            "IRR Source 5,irr-source-5,http://irr5.example.com/,1440",
            "IRR Source 6,irr-source-6,http://irr6.example.com/,1440",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{irr_sources[0].pk},Primary IRR Updated,Updated",
            f"{irr_sources[1].pk},Secondary IRR Updated,Updated",
            f"{irr_sources[2].pk},Tertiary IRR Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "enabled": False,
        }


class IRRPrefixListConfigTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = IRRPrefixListConfig

    @classmethod
    def setUpTestData(cls):
        irr_source = IRRSource.objects.create(name="Test IRR", slug="test-irr", url="http://irr.example.com/")

        prefix_lists = (
            PrefixList(name="PL 1", family=4),
            PrefixList(name="PL 2", family=4),
            PrefixList(name="PL 3", family=6),
            PrefixList(name="PL 4", family=4),
        )
        PrefixList.objects.bulk_create(prefix_lists)

        configs = (
            IRRPrefixListConfig(prefix_list=prefix_lists[0], irr_source=irr_source, source_as_set="AS-TEST1"),
            IRRPrefixListConfig(prefix_list=prefix_lists[1], irr_source=irr_source, source_as_set="AS-TEST2"),
            IRRPrefixListConfig(prefix_list=prefix_lists[2], irr_source=irr_source, source_as_set="AS-TEST3"),
        )
        IRRPrefixListConfig.objects.bulk_create(configs)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "prefix_list": prefix_lists[3].pk,
            "irr_source": irr_source.pk,
            "source_as_set": "AS-NEW",
            "sync_interval": 720,
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "prefix_list,irr_source,source_as_set,sync_interval",
            f"{prefix_lists[3].name},{irr_source.name},AS-CSV1,1440",
        )

        cls.csv_update_data = (
            "id,source_as_set",
            f"{configs[0].pk},AS-UPDATED1",
            f"{configs[1].pk},AS-UPDATED2",
            f"{configs[2].pk},AS-UPDATED3",
        )

        cls.bulk_edit_data = {
            "sync_interval": 2880,
        }


class PeeringSessionTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = PeeringSession

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="Test RIR", is_private=True)
        remote_asns = (
            ASN(asn=65001, rir=rir),
            ASN(asn=65002, rir=rir),
            ASN(asn=65003, rir=rir),
            ASN(asn=65004, rir=rir),
        )
        ASN.objects.bulk_create(remote_asns)

        ips = (
            IPAddress(address="192.0.2.1/32"),
            IPAddress(address="192.0.2.2/32"),
            IPAddress(address="192.0.2.3/32"),
            IPAddress(address="192.0.2.4/32"),
        )
        IPAddress.objects.bulk_create(ips)

        bgp_peers = (
            BGPPeer(name="Peer 1", peer=ips[0], remote_as=remote_asns[0]),
            BGPPeer(name="Peer 2", peer=ips[1], remote_as=remote_asns[1]),
            BGPPeer(name="Peer 3", peer=ips[2], remote_as=remote_asns[2]),
            BGPPeer(name="Peer 4", peer=ips[3], remote_as=remote_asns[3]),
        )
        BGPPeer.objects.bulk_create(bgp_peers)

        relationship = Relationship.objects.create(name="Peer", slug="peer")

        sessions = (
            PeeringSession(bgp_peer=bgp_peers[0], relationship=relationship),
            PeeringSession(bgp_peer=bgp_peers[1], relationship=relationship),
            PeeringSession(bgp_peer=bgp_peers[2], relationship=relationship),
        )
        PeeringSession.objects.bulk_create(sessions)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "bgp_peer": bgp_peers[3].pk,
            "relationship": relationship.pk,
            "service_reference": "TICKET-999",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "bgp_peer,service_reference",
            f"{bgp_peers[3].name},CSV-REF",
        )

        cls.csv_update_data = (
            "id,service_reference",
            f"{sessions[0].pk},REF-1",
            f"{sessions[1].pk},REF-2",
            f"{sessions[2].pk},REF-3",
        )

        cls.bulk_edit_data = {
            "service_reference": "BULK-REF",
        }


class PeeringFabricTypeTestCase(PluginURLMixin, ViewTestCases.OrganizationalObjectViewTestCase):
    model = PeeringFabricType

    @classmethod
    def setUpTestData(cls):
        fabric_types = (
            PeeringFabricType(name="Internet Exchange", slug="internet-exchange", color="ff0000"),
            PeeringFabricType(name="Cloud Exchange", slug="cloud-exchange", color="00ff00"),
            PeeringFabricType(name="Private LAN", slug="private-lan", color="0000ff"),
        )
        PeeringFabricType.objects.bulk_create(fabric_types)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Fabric Type",
            "slug": "new-fabric-type",
            "color": "ffff00",
            "description": "A new fabric type",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,color",
            "Fabric Type 4,fabric-type-4,aabbcc",
            "Fabric Type 5,fabric-type-5,ddeeff",
            "Fabric Type 6,fabric-type-6,112233",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{fabric_types[0].pk},IX Updated,Updated",
            f"{fabric_types[1].pk},Cloud Updated,Updated",
            f"{fabric_types[2].pk},Private Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class PeeringFabricTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = PeeringFabric

    @classmethod
    def setUpTestData(cls):
        fabric_type = PeeringFabricType.objects.create(name="Internet Exchange", slug="internet-exchange")

        fabrics = (
            PeeringFabric(name="DE-CIX Frankfurt", slug="de-cix-fra", type=fabric_type),
            PeeringFabric(name="AMS-IX", slug="ams-ix", type=fabric_type),
            PeeringFabric(name="LINX", slug="linx", type=fabric_type),
        )
        PeeringFabric.objects.bulk_create(fabrics)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Fabric",
            "slug": "new-fabric",
            "type": fabric_type.pk,
            "status": "active",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,status",
            "Fabric 4,fabric-4,active",
            "Fabric 5,fabric-5,active",
            "Fabric 6,fabric-6,planned",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{fabrics[0].pk},DE-CIX Updated,Updated",
            f"{fabrics[1].pk},AMS-IX Updated,Updated",
            f"{fabrics[2].pk},LINX Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class PeerASNTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = PeerASN

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="RFC 6996", is_private=True)

        asns = (
            ASN(asn=65001, rir=rir, description="Peer 1"),
            ASN(asn=65002, rir=rir, description="Peer 2"),
            ASN(asn=65003, rir=rir, description="Peer 3"),
            ASN(asn=65004, rir=rir, description="Peer 4"),
        )
        ASN.objects.bulk_create(asns)

        peer_asns = (
            PeerASN(asn=asns[0]),
            PeerASN(asn=asns[1]),
            PeerASN(asn=asns[2]),
        )
        PeerASN.objects.bulk_create(peer_asns)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "asn": asns[3].pk,
            "affiliated": False,
            "irr_as_set": "AS-TEST",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "asn",
            f"{asns[3].asn}",
        )

        cls.csv_update_data = (
            "id,irr_as_set",
            f"{peer_asns[0].pk},AS-PEER1",
            f"{peer_asns[1].pk},AS-PEER2",
            f"{peer_asns[2].pk},AS-PEER3",
        )

        cls.bulk_edit_data = {
            "affiliated": True,
            "irr_as_set": "AS-BULK",
        }


class PeeringNetworkTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = PeeringNetwork

    @classmethod
    def setUpTestData(cls):
        fabric_type = PeeringFabricType.objects.create(name="Internet Exchange", slug="internet-exchange")
        fabric = PeeringFabric.objects.create(name="Test IX", slug="test-ix", type=fabric_type)

        prefixes = (
            Prefix(prefix="192.0.2.0/24"),
            Prefix(prefix="198.51.100.0/24"),
            Prefix(prefix="203.0.113.0/24"),
            Prefix(prefix="10.0.0.0/24"),
        )
        Prefix.objects.bulk_create(prefixes)

        networks = (
            PeeringNetwork(name="Peering LAN 1", fabric=fabric, prefix=prefixes[0]),
            PeeringNetwork(name="Peering LAN 2", fabric=fabric, prefix=prefixes[1]),
            PeeringNetwork(name="Peering LAN 3", fabric=fabric, prefix=prefixes[2]),
        )
        PeeringNetwork.objects.bulk_create(networks)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Peering LAN",
            "fabric": fabric.pk,
            "prefix": prefixes[3].pk,
            "status": "active",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,fabric,prefix,status",
            f"Peering LAN 4,{fabric.name},{prefixes[3].prefix},active",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{networks[0].pk},Peering LAN 1 Updated,Updated",
            f"{networks[1].pk},Peering LAN 2 Updated,Updated",
            f"{networks[2].pk},Peering LAN 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "status": "decommissioned",
        }


class PeeringConnectionTestCase(PluginURLMixin, ViewTestCases.PrimaryObjectViewTestCase):
    model = PeeringConnection

    @classmethod
    def setUpTestData(cls):
        fabric_type = PeeringFabricType.objects.create(name="Internet Exchange", slug="internet-exchange")
        fabric = PeeringFabric.objects.create(name="Test IX", slug="test-ix", type=fabric_type)

        prefixes = (
            Prefix(prefix="192.0.2.0/24"),
            Prefix(prefix="198.51.100.0/24"),
        )
        Prefix.objects.bulk_create(prefixes)

        network = PeeringNetwork.objects.create(name="Peering LAN", fabric=fabric, prefix=prefixes[0])

        site = Site.objects.create(name="Test Site", slug="test-site")
        manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Test Model", slug="test-model")
        device_role = DeviceRole.objects.create(name="Test Role", slug="test-role")
        device = Device.objects.create(name="Device 1", site=site, device_type=device_type, role=device_role)

        interfaces = (
            Interface(name="eth0", device=device, type="1000base-t"),
            Interface(name="eth1", device=device, type="1000base-t"),
            Interface(name="eth2", device=device, type="1000base-t"),
            Interface(name="eth3", device=device, type="1000base-t"),
        )
        Interface.objects.bulk_create(interfaces)

        connections = (
            PeeringConnection(peering_network=network, interface=interfaces[0]),
            PeeringConnection(peering_network=network, interface=interfaces[1]),
            PeeringConnection(peering_network=network, interface=interfaces[2]),
        )
        PeeringConnection.objects.bulk_create(connections)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "peering_network": network.pk,
            "interface": interfaces[3].pk,
            "status": "active",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "peering_network,interface,status",
            f"{network.name},{interfaces[3].pk},active",
        )

        cls.csv_update_data = (
            "id,description",
            f"{connections[0].pk},Updated",
            f"{connections[1].pk},Updated",
            f"{connections[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "status": "decommissioned",
        }
