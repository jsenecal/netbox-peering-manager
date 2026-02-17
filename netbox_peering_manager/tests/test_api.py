from django.urls import reverse
from ipam.models import ASN, RIR, IPAddress
from netbox_routing.models import BGPPeer, PrefixList
from utilities.testing import APITestCase, APIViewTestCases

from netbox_peering_manager.models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringSession,
    Relationship,
)


class PeerASNAPITestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    APIViewTestCases.GraphQLTestCase,
):
    model = PeerASN
    view_namespace = "plugins-api:netbox_peering_manager"
    brief_fields = ["affiliated", "asn", "display", "id", "url"]
    graphql_base_name = "netbox_peering_manager_peer_asn"

    bulk_update_data = {
        "affiliated": True,
    }
    user_permissions = ["ipam.view_asn"]

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="Test RIR API", slug="test-rir-api")
        asns = [
            ASN.objects.create(asn=65100, rir=rir),
            ASN.objects.create(asn=65101, rir=rir),
            ASN.objects.create(asn=65102, rir=rir),
            ASN.objects.create(asn=65103, rir=rir),
            ASN.objects.create(asn=65104, rir=rir),
            ASN.objects.create(asn=65105, rir=rir),
        ]
        PeerASN.objects.create(asn=asns[0])
        PeerASN.objects.create(asn=asns[1])
        PeerASN.objects.create(asn=asns[2])

        cls.create_data = [
            {"asn": asns[3].pk},
            {"asn": asns[4].pk},
            {"asn": asns[5].pk},
        ]


class IRRPrefixListConfigAPITestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = IRRPrefixListConfig
    view_namespace = "plugins-api:netbox_peering_manager"
    brief_fields = ["display", "id", "prefix_list", "source_as_set", "url"]

    bulk_update_data = {
        "sync_interval": 2880,
    }
    user_permissions = ["netbox_routing.view_prefixlist"]

    @classmethod
    def setUpTestData(cls):
        irr_source = IRRSource.objects.create(name="Test IRR", slug="test-irr", url="http://irr.example.com/")
        prefix_lists = [PrefixList.objects.create(name=f"PL {i}", family=4) for i in range(6)]

        IRRPrefixListConfig.objects.create(prefix_list=prefix_lists[0], irr_source=irr_source, source_as_set="AS-TEST1")
        IRRPrefixListConfig.objects.create(prefix_list=prefix_lists[1], irr_source=irr_source, source_as_set="AS-TEST2")
        IRRPrefixListConfig.objects.create(prefix_list=prefix_lists[2], irr_source=irr_source, source_as_set="AS-TEST3")

        cls.create_data = [
            {"prefix_list": prefix_lists[3].pk, "irr_source": irr_source.pk, "source_as_set": "AS-NEW1"},
            {"prefix_list": prefix_lists[4].pk, "irr_source": irr_source.pk, "source_as_set": "AS-NEW2"},
            {"prefix_list": prefix_lists[5].pk, "irr_source": irr_source.pk, "source_as_set": "AS-NEW3"},
        ]


class PeeringSessionAPITestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = PeeringSession
    view_namespace = "plugins-api:netbox_peering_manager"
    brief_fields = ["bgp_peer", "display", "id", "relationship", "url"]

    bulk_update_data = {
        "service_reference": "BULK-REF",
    }
    user_permissions = ["netbox_routing.view_bgppeer"]

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="Test RIR", slug="test-rir-api")
        relationship = Relationship.objects.create(name="Peer", slug="peer")

        asns = [ASN.objects.create(asn=65100 + i, rir=rir) for i in range(6)]
        ips = [IPAddress.objects.create(address=f"192.0.2.{i + 1}/32") for i in range(6)]

        bgp_peers = [BGPPeer.objects.create(name=f"Peer {i}", peer=ips[i], remote_as=asns[i]) for i in range(6)]

        PeeringSession.objects.create(bgp_peer=bgp_peers[0], relationship=relationship)
        PeeringSession.objects.create(bgp_peer=bgp_peers[1], relationship=relationship)
        PeeringSession.objects.create(bgp_peer=bgp_peers[2], relationship=relationship)

        cls.create_data = [
            {"bgp_peer": bgp_peers[3].pk, "relationship": relationship.pk},
            {"bgp_peer": bgp_peers[4].pk, "relationship": relationship.pk},
            {"bgp_peer": bgp_peers[5].pk, "relationship": relationship.pk},
        ]


class TestAPISchema(APITestCase):
    def test_api_schema(self):
        url = reverse("plugins-api:netbox_peering_manager-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)
        self.assertEqual(response.status_code, 200)
