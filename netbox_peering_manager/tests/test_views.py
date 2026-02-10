"""View tests for netbox_peering_manager plugin."""

from ipam.models import ASN, RIR
from utilities.testing import ViewTestCases, create_tags

from netbox_peering_manager.models import (
    BFD,
    ASPathList,
    BGPPeerGroup,
    Community,
    CommunityList,
    IRRSource,
    PeerASN,
    PeeringFabric,
    PeeringFabricType,
    PrefixList,
    Relationship,
    RoutingPolicy,
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
