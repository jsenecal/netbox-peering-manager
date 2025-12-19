from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework.routers import APIRootView

from netbox_peering_manager.filtersets import (
    ASPathListFilterSet,
    ASPathListRuleFilterSet,
    BFDFilterSet,
    BGPPeerGroupFilterSet,
    BGPSessionFilterSet,
    CommunityFilterSet,
    CommunityListFilterSet,
    CommunityListRuleFilterSet,
    PeeringConnectionFilterSet,
    PeeringFabricFilterSet,
    PeeringFabricTypeFilterSet,
    PeeringNetworkFilterSet,
    PrefixListFilterSet,
    PrefixListRuleFilterSet,
    RelationshipFilterSet,
    RoutingPolicyFilterSet,
    RoutingPolicyRuleFilterSet,
)
from netbox_peering_manager.models import (
    BFD,
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
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

from .serializers import (
    ASPathListRuleSerializer,
    ASPathListSerializer,
    BFDSerializer,
    BGPPeerGroupSerializer,
    BGPSessionSerializer,
    CommunityListRuleSerializer,
    CommunityListSerializer,
    CommunitySerializer,
    PeeringConnectionSerializer,
    PeeringFabricSerializer,
    PeeringFabricTypeSerializer,
    PeeringNetworkSerializer,
    PrefixListRuleSerializer,
    PrefixListSerializer,
    RelationshipSerializer,
    RoutingPolicyRuleSerializer,
    RoutingPolicySerializer,
)


class RootView(APIRootView):
    def get_view_name(self):
        return "Peering Manager"


class RelationshipViewSet(NetBoxModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    filterset_class = RelationshipFilterSet


class BFDViewSet(NetBoxModelViewSet):
    queryset = BFD.objects.all()
    serializer_class = BFDSerializer
    filterset_class = BFDFilterSet


class BGPSessionViewSet(NetBoxModelViewSet):
    queryset = BGPSession.objects.all()
    serializer_class = BGPSessionSerializer
    filterset_class = BGPSessionFilterSet


class RoutingPolicyViewSet(NetBoxModelViewSet):
    queryset = RoutingPolicy.objects.all()
    serializer_class = RoutingPolicySerializer
    filterset_class = RoutingPolicyFilterSet


class RoutingPolicyRuleViewSet(NetBoxModelViewSet):
    queryset = RoutingPolicyRule.objects.all()
    serializer_class = RoutingPolicyRuleSerializer
    filterset_class = RoutingPolicyRuleFilterSet


class BGPPeerGroupViewSet(NetBoxModelViewSet):
    queryset = BGPPeerGroup.objects.all()
    serializer_class = BGPPeerGroupSerializer
    filterset_class = BGPPeerGroupFilterSet


class CommunityViewSet(NetBoxModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    filterset_class = CommunityFilterSet


class CommunityListViewSet(NetBoxModelViewSet):
    queryset = CommunityList.objects.all()
    serializer_class = CommunityListSerializer
    filterset_class = CommunityListFilterSet


class CommunityListRuleViewSet(NetBoxModelViewSet):
    queryset = CommunityListRule.objects.all()
    serializer_class = CommunityListRuleSerializer
    filterset_class = CommunityListRuleFilterSet


class PrefixListViewSet(NetBoxModelViewSet):
    queryset = PrefixList.objects.all()
    serializer_class = PrefixListSerializer
    filterset_class = PrefixListFilterSet


class PrefixListRuleViewSet(NetBoxModelViewSet):
    queryset = PrefixListRule.objects.all()
    serializer_class = PrefixListRuleSerializer
    filterset_class = PrefixListRuleFilterSet


class ASPathListViewSet(NetBoxModelViewSet):
    queryset = ASPathList.objects.all()
    serializer_class = ASPathListSerializer
    filterset_class = ASPathListFilterSet


class ASPathListRuleViewSet(NetBoxModelViewSet):
    queryset = ASPathListRule.objects.all()
    serializer_class = ASPathListRuleSerializer
    filterset_class = ASPathListRuleFilterSet


# =============================================================================
# Peering Fabric ViewSets
# =============================================================================


class PeeringFabricTypeViewSet(NetBoxModelViewSet):
    queryset = PeeringFabricType.objects.all()
    serializer_class = PeeringFabricTypeSerializer
    filterset_class = PeeringFabricTypeFilterSet


class PeeringFabricViewSet(NetBoxModelViewSet):
    queryset = PeeringFabric.objects.all()
    serializer_class = PeeringFabricSerializer
    filterset_class = PeeringFabricFilterSet


class PeeringNetworkViewSet(NetBoxModelViewSet):
    queryset = PeeringNetwork.objects.all()
    serializer_class = PeeringNetworkSerializer
    filterset_class = PeeringNetworkFilterSet


class PeeringConnectionViewSet(NetBoxModelViewSet):
    queryset = PeeringConnection.objects.all()
    serializer_class = PeeringConnectionSerializer
    filterset_class = PeeringConnectionFilterSet
