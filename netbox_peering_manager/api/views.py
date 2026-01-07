from django.db.models import Count
from extras.api.mixins import ConfigTemplateRenderMixin
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView

from netbox_peering_manager.filtersets import (
    ASPathListFilterSet,
    ASPathListRuleFilterSet,
    BFDFilterSet,
    BGPPeerGroupFilterSet,
    BGPSessionFilterSet,
    CommunityFilterSet,
    CommunityListFilterSet,
    CommunityListRuleFilterSet,
    IRRSourceFilterSet,
    PeerASNFilterSet,
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
from netbox_peering_manager.services.config_renderer import ConfigRenderer

from .serializers import (
    ASPathListRuleSerializer,
    ASPathListSerializer,
    BFDSerializer,
    BGPPeerGroupSerializer,
    BGPSessionSerializer,
    CommunityListRuleSerializer,
    CommunityListSerializer,
    CommunitySerializer,
    IRRSourceSerializer,
    PeerASNSerializer,
    PeeringConnectionSerializer,
    PeeringFabricSerializer,
    PeeringFabricTypeSerializer,
    PeeringNetworkSerializer,
    PrefixListRuleSerializer,
    PrefixListSerializer,
    RelationshipSerializer,
    RenderConfigRequestSerializer,
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


class IRRSourceViewSet(NetBoxModelViewSet):
    queryset = IRRSource.objects.all()
    serializer_class = IRRSourceSerializer
    filterset_class = IRRSourceFilterSet


class PeerASNViewSet(NetBoxModelViewSet):
    queryset = PeerASN.objects.annotate(session_count=Count("sessions"))
    serializer_class = PeerASNSerializer
    filterset_class = PeerASNFilterSet


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


# =============================================================================
# Configuration Templating Views
# =============================================================================


class RenderConfigView(ConfigTemplateRenderMixin, APIView):
    """
    Render a ConfigTemplate with BGP session context.
    POST /api/plugins/bgp/render-config/
    """

    renderer_classes = [JSONRenderer, TextRenderer]
    _ignore_model_permissions = True

    def post(self, request):
        serializer = RenderConfigRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        template = serializer.validated_data["template"]
        device = serializer.validated_data.get("device")
        sessions = serializer.validated_data.get("sessions", [])

        # Build context
        renderer = ConfigRenderer()
        context = renderer.build_context(
            device=device,
            sessions=sessions if sessions else None,
        )

        # Render template using NetBox's mixin
        response = self.render_configtemplate(request, template, context)

        # Add context if requested
        if request.query_params.get("include_context") == "true" and isinstance(response.data, dict):
            response.data["context"] = context

        # Add metadata
        if isinstance(response.data, dict):
            if device:
                response.data["device"] = {"id": device.pk, "name": device.name}
            response.data["session_count"] = len(context["sessions"])

        return response
