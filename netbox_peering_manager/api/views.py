from netbox.api.viewsets import NetBoxModelViewSet

from .serializers import (
    BGPSessionSerializer,
    RoutingPolicySerializer,
    BGPPeerGroupSerializer,
    BGPCommunitySerializer,
    PrefixListSerializer,
    PrefixListRuleSerializer,
    RoutingPolicyRuleSerializer,
)
from netbox_peering_manager.models import (
    BGPSession,
    RoutingPolicy,
    BGPPeerGroup,
    BGPCommunity,
    PrefixList,
    PrefixListRule,
    RoutingPolicyRule,
)
from netbox_peering_manager.filters import (
    BGPSessionFilterSet,
    RoutingPolicyFilterSet,
    BGPPeerGroupFilterSet,
    CommunityFilterSet,
    PrefixListFilterSet,
    PrefixListRuleFilterSet,
    RoutingPolicyRuleFilterSet,
)


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
    queryset = BGPCommunity.objects.all()
    serializer_class = BGPCommunitySerializer
    filterset_class = CommunityFilterSet


class PrefixListViewSet(NetBoxModelViewSet):
    queryset = PrefixList.objects.all()
    serializer_class = PrefixListSerializer
    filterset_class = PrefixListFilterSet


class PrefixListRuleViewSet(NetBoxModelViewSet):
    queryset = PrefixListRule.objects.all()
    serializer_class = PrefixListRuleSerializer
    filterset_class = PrefixListRuleFilterSet
