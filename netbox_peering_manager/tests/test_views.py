"""View tests for netbox_peering_manager plugin."""

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import ASN, RIR, IPAddress, Prefix
from utilities.testing import ViewTestCases, create_tags

from netbox_peering_manager.models import (
    BFD,
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PrefixList,
    PrefixListRule,
    Relationship,
    RoutingPolicy,
    RoutingPolicyRule,
)


class RelationshipTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for Relationship views."""

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


class BFDTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for BFD views."""

    model = BFD

    @classmethod
    def setUpTestData(cls):
        bfd_profiles = (
            BFD(name="Fast", minimum_transmit_interval=100, minimum_receive_interval=100, detect_multiplier=3),
            BFD(name="Normal", minimum_transmit_interval=300, minimum_receive_interval=300, detect_multiplier=3),
            BFD(name="Slow", minimum_transmit_interval=1000, minimum_receive_interval=1000, detect_multiplier=5),
        )
        BFD.objects.bulk_create(bfd_profiles)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Custom BFD",
            "minimum_transmit_interval": 500,
            "minimum_receive_interval": 500,
            "detect_multiplier": 4,
            "description": "Custom BFD profile",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,minimum_transmit_interval,minimum_receive_interval,detect_multiplier",
            "BFD Profile 1,200,200,3",
            "BFD Profile 2,400,400,4",
            "BFD Profile 3,600,600,5",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{bfd_profiles[0].pk},Fast Updated,Updated",
            f"{bfd_profiles[1].pk},Normal Updated,Updated",
            f"{bfd_profiles[2].pk},Slow Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class IRRSourceTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for IRRSource views."""

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
            "name,slug,url",
            "IRR Source 4,irr-source-4,http://irr4.example.com/",
            "IRR Source 5,irr-source-5,http://irr5.example.com/",
            "IRR Source 6,irr-source-6,http://irr6.example.com/",
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


class RoutingPolicyTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for RoutingPolicy views."""

    model = RoutingPolicy

    @classmethod
    def setUpTestData(cls):
        policies = (
            RoutingPolicy(name="Import Policy 1", weight=100),
            RoutingPolicy(name="Export Policy 1", weight=200),
            RoutingPolicy(name="Default Policy", weight=0),
        )
        RoutingPolicy.objects.bulk_create(policies)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Policy",
            "description": "A new routing policy",
            "weight": 150,
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,weight",
            "Policy 4,100",
            "Policy 5,200",
            "Policy 6,300",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{policies[0].pk},Import Policy Updated,Updated",
            f"{policies[1].pk},Export Policy Updated,Updated",
            f"{policies[2].pk},Default Policy Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class BGPPeerGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for BGPPeerGroup views."""

    model = BGPPeerGroup

    @classmethod
    def setUpTestData(cls):
        peer_groups = (
            BGPPeerGroup(name="Transit Peers"),
            BGPPeerGroup(name="IXP Peers"),
            BGPPeerGroup(name="Customer Peers"),
        )
        BGPPeerGroup.objects.bulk_create(peer_groups)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Peer Group",
            "description": "A new peer group",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description",
            "Peer Group 4,Description 4",
            "Peer Group 5,Description 5",
            "Peer Group 6,Description 6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{peer_groups[0].pk},Transit Peers Updated,Updated",
            f"{peer_groups[1].pk},IXP Peers Updated,Updated",
            f"{peer_groups[2].pk},Customer Peers Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class CommunityTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for Community views."""

    model = Community

    @classmethod
    def setUpTestData(cls):
        communities = (
            Community(value="65000:100"),
            Community(value="65000:200"),
            Community(value="65000:300"),
        )
        Community.objects.bulk_create(communities)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "value": "65000:400",
            "description": "New community",
            "status": "active",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "value,status",
            "65000:500,active",
            "65000:600,active",
            "65000:700,active",
        )

        cls.csv_update_data = (
            "id,value,description",
            f"{communities[0].pk},65000:100,Updated",
            f"{communities[1].pk},65000:200,Updated",
            f"{communities[2].pk},65000:300,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class CommunityListTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for CommunityList views."""

    model = CommunityList

    @classmethod
    def setUpTestData(cls):
        community_lists = (
            CommunityList(name="Community List 1"),
            CommunityList(name="Community List 2"),
            CommunityList(name="Community List 3"),
        )
        CommunityList.objects.bulk_create(community_lists)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Community List",
            "description": "A new community list",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description",
            "Community List 4,Description 4",
            "Community List 5,Description 5",
            "Community List 6,Description 6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{community_lists[0].pk},Community List 1 Updated,Updated",
            f"{community_lists[1].pk},Community List 2 Updated,Updated",
            f"{community_lists[2].pk},Community List 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class ASPathListTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for ASPathList views."""

    model = ASPathList

    @classmethod
    def setUpTestData(cls):
        aspath_lists = (
            ASPathList(name="AS Path List 1"),
            ASPathList(name="AS Path List 2"),
            ASPathList(name="AS Path List 3"),
        )
        ASPathList.objects.bulk_create(aspath_lists)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New AS Path List",
            "description": "A new AS path list",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description",
            "AS Path List 4,Description 4",
            "AS Path List 5,Description 5",
            "AS Path List 6,Description 6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{aspath_lists[0].pk},AS Path List 1 Updated,Updated",
            f"{aspath_lists[1].pk},AS Path List 2 Updated,Updated",
            f"{aspath_lists[2].pk},AS Path List 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class PrefixListTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for PrefixList views."""

    model = PrefixList

    @classmethod
    def setUpTestData(cls):
        prefix_lists = (
            PrefixList(name="Prefix List 1", family=4),
            PrefixList(name="Prefix List 2", family=4),
            PrefixList(name="Prefix List 3", family=6),
        )
        PrefixList.objects.bulk_create(prefix_lists)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Prefix List",
            "family": 4,
            "description": "A new prefix list",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,family",
            "Prefix List 4,4",
            "Prefix List 5,4",
            "Prefix List 6,6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{prefix_lists[0].pk},Prefix List 1 Updated,Updated",
            f"{prefix_lists[1].pk},Prefix List 2 Updated,Updated",
            f"{prefix_lists[2].pk},Prefix List 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class PeeringFabricTypeTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test cases for PeeringFabricType views."""

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


class PeeringFabricTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for PeeringFabric views."""

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


class PeerASNTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for PeerASN views."""

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
            f"{asns[3].pk}",
        )

        cls.csv_update_data = (
            "id,irr_as_set,comments",
            f"{peer_asns[0].pk},AS-PEER1,Updated",
            f"{peer_asns[1].pk},AS-PEER2,Updated",
            f"{peer_asns[2].pk},AS-PEER3,Updated",
        )

        cls.bulk_edit_data = {
            "affiliated": True,
            "comments": "Bulk updated",
        }


class BGPSessionTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for BGPSession views."""

    model = BGPSession

    @classmethod
    def setUpTestData(cls):
        # Create required dependencies
        site = Site.objects.create(name="Test Site", slug="test-site")
        manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Test Model", slug="test-model")
        device_role = DeviceRole.objects.create(name="Test Role", slug="test-role")

        devices = (
            Device(name="Device 1", site=site, device_type=device_type, role=device_role),
            Device(name="Device 2", site=site, device_type=device_type, role=device_role),
        )
        Device.objects.bulk_create(devices)

        rir = RIR.objects.create(name="RFC 6996", is_private=True)

        # Create ASNs
        local_asns = (
            ASN(asn=65000, rir=rir, description="Local AS 1"),
            ASN(asn=65001, rir=rir, description="Local AS 2"),
        )
        ASN.objects.bulk_create(local_asns)

        remote_asns = (
            ASN(asn=65100, rir=rir, description="Remote AS 1"),
            ASN(asn=65101, rir=rir, description="Remote AS 2"),
            ASN(asn=65102, rir=rir, description="Remote AS 3"),
            ASN(asn=65103, rir=rir, description="Remote AS 4"),
        )
        ASN.objects.bulk_create(remote_asns)

        peer_asns = (
            PeerASN(asn=remote_asns[0]),
            PeerASN(asn=remote_asns[1]),
            PeerASN(asn=remote_asns[2]),
            PeerASN(asn=remote_asns[3]),
        )
        PeerASN.objects.bulk_create(peer_asns)

        # Create IP addresses
        local_ips = (
            IPAddress(address="192.0.2.1/24"),
            IPAddress(address="192.0.2.2/24"),
            IPAddress(address="192.0.2.3/24"),
            IPAddress(address="192.0.2.4/24"),
        )
        IPAddress.objects.bulk_create(local_ips)

        remote_ips = (
            IPAddress(address="198.51.100.1/24"),
            IPAddress(address="198.51.100.2/24"),
            IPAddress(address="198.51.100.3/24"),
            IPAddress(address="198.51.100.4/24"),
        )
        IPAddress.objects.bulk_create(remote_ips)

        # Create BGP sessions
        sessions = (
            BGPSession(
                name="Session 1",
                device=devices[0],
                local_address=local_ips[0],
                remote_address=remote_ips[0],
                local_as=local_asns[0],
                remote_as=peer_asns[0],
            ),
            BGPSession(
                name="Session 2",
                device=devices[0],
                local_address=local_ips[1],
                remote_address=remote_ips[1],
                local_as=local_asns[0],
                remote_as=peer_asns[1],
            ),
            BGPSession(
                name="Session 3",
                device=devices[1],
                local_address=local_ips[2],
                remote_address=remote_ips[2],
                local_as=local_asns[1],
                remote_as=peer_asns[2],
            ),
        )
        BGPSession.objects.bulk_create(sessions)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "New Session",
            "device": devices[1].pk,
            "local_address": local_ips[3].pk,
            "remote_address": remote_ips[3].pk,
            "local_as": local_asns[1].pk,
            "remote_as": peer_asns[3].pk,
            "status": "active",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,device,local_address,remote_address,local_as,remote_as,status",
            f"Session 4,{devices[0].pk},{local_ips[3].pk},{remote_ips[3].pk},{local_asns[0].pk},{peer_asns[3].pk},active",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{sessions[0].pk},Session 1 Updated,Updated",
            f"{sessions[1].pk},Session 2 Updated,Updated",
            f"{sessions[2].pk},Session 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "status": "disabled",
        }


class PeeringNetworkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for PeeringNetwork views."""

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
            f"Peering LAN 4,{fabric.pk},{prefixes[3].pk},active",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{networks[0].pk},Peering LAN 1 Updated,Updated",
            f"{networks[1].pk},Peering LAN 2 Updated,Updated",
            f"{networks[2].pk},Peering LAN 3 Updated,Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "status": "disabled",
        }


class PeeringConnectionTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for PeeringConnection views."""

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
            f"{network.pk},{interfaces[3].pk},active",
        )

        cls.csv_update_data = (
            "id,description",
            f"{connections[0].pk},Updated",
            f"{connections[1].pk},Updated",
            f"{connections[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
            "status": "disabled",
        }


class ASPathListRuleTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for ASPathListRule views."""

    model = ASPathListRule

    @classmethod
    def setUpTestData(cls):
        aspath_list = ASPathList.objects.create(name="Test AS Path List")

        rules = (
            ASPathListRule(aspath_list=aspath_list, index=10, action="permit", pattern="^65000$"),
            ASPathListRule(aspath_list=aspath_list, index=20, action="permit", pattern="^65001$"),
            ASPathListRule(aspath_list=aspath_list, index=30, action="deny", pattern=".*"),
        )
        ASPathListRule.objects.bulk_create(rules)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aspath_list": aspath_list.pk,
            "index": 40,
            "action": "permit",
            "pattern": "^65002_",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "aspath_list,index,action,pattern",
            f"{aspath_list.pk},50,permit,^65003$",
            f"{aspath_list.pk},60,permit,^65004$",
            f"{aspath_list.pk},70,deny,.*",
        )

        cls.csv_update_data = (
            "id,description",
            f"{rules[0].pk},Updated",
            f"{rules[1].pk},Updated",
            f"{rules[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class PrefixListRuleTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for PrefixListRule views."""

    model = PrefixListRule

    @classmethod
    def setUpTestData(cls):
        prefix_list = PrefixList.objects.create(name="Test Prefix List", family=4)

        rules = (
            PrefixListRule(prefix_list=prefix_list, index=10, action="permit", prefix_custom="192.0.2.0/24"),
            PrefixListRule(prefix_list=prefix_list, index=20, action="permit", prefix_custom="198.51.100.0/24"),
            PrefixListRule(prefix_list=prefix_list, index=30, action="deny", prefix_custom="0.0.0.0/0", le=32),
        )
        PrefixListRule.objects.bulk_create(rules)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "prefix_list": prefix_list.pk,
            "index": 40,
            "action": "permit",
            "prefix_custom": "203.0.113.0/24",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "prefix_list,index,action,prefix_custom",
            f"{prefix_list.pk},50,permit,10.0.0.0/8",
            f"{prefix_list.pk},60,permit,172.16.0.0/12",
            f"{prefix_list.pk},70,deny,0.0.0.0/0",
        )

        cls.csv_update_data = (
            "id,description",
            f"{rules[0].pk},Updated",
            f"{rules[1].pk},Updated",
            f"{rules[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class CommunityListRuleTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for CommunityListRule views."""

    model = CommunityListRule

    @classmethod
    def setUpTestData(cls):
        community_list = CommunityList.objects.create(name="Test Community List")

        communities = (
            Community(value="65000:100"),
            Community(value="65000:200"),
            Community(value="65000:300"),
            Community(value="65000:400"),
        )
        Community.objects.bulk_create(communities)

        rules = (
            CommunityListRule(community_list=community_list, action="permit", community=communities[0]),
            CommunityListRule(community_list=community_list, action="permit", community=communities[1]),
            CommunityListRule(community_list=community_list, action="deny", community=communities[2]),
        )
        CommunityListRule.objects.bulk_create(rules)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "community_list": community_list.pk,
            "action": "permit",
            "community": communities[3].pk,
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "community_list,action,community",
            f"{community_list.pk},permit,{communities[3].pk}",
        )

        cls.csv_update_data = (
            "id,description",
            f"{rules[0].pk},Updated",
            f"{rules[1].pk},Updated",
            f"{rules[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }


class RoutingPolicyRuleTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test cases for RoutingPolicyRule views."""

    model = RoutingPolicyRule

    @classmethod
    def setUpTestData(cls):
        routing_policy = RoutingPolicy.objects.create(name="Test Routing Policy")

        rules = (
            RoutingPolicyRule(routing_policy=routing_policy, index=10, action="permit"),
            RoutingPolicyRule(routing_policy=routing_policy, index=20, action="permit"),
            RoutingPolicyRule(routing_policy=routing_policy, index=30, action="deny"),
        )
        RoutingPolicyRule.objects.bulk_create(rules)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "routing_policy": routing_policy.pk,
            "index": 40,
            "action": "permit",
            "description": "New rule",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "routing_policy,index,action",
            f"{routing_policy.pk},50,permit",
            f"{routing_policy.pk},60,permit",
            f"{routing_policy.pk},70,deny",
        )

        cls.csv_update_data = (
            "id,description",
            f"{rules[0].pk},Updated",
            f"{rules[1].pk},Updated",
            f"{rules[2].pk},Updated",
        )

        cls.bulk_edit_data = {
            "description": "Bulk updated",
        }
