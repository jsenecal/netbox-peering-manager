from extras.api.mixins import ConfigTemplateRenderMixin
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView

from netbox_peering_manager.filtersets import (
    IRRPrefixListConfigFilterSet,
    IRRSourceFilterSet,
    PeerASNFilterSet,
    PeeringConnectionFilterSet,
    PeeringFabricFilterSet,
    PeeringFabricTypeFilterSet,
    PeeringNetworkFilterSet,
    PeeringSessionFilterSet,
    RelationshipFilterSet,
)
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
from netbox_peering_manager.services.config_renderer import ConfigRenderer

from .serializers import (
    IRRPrefixListConfigSerializer,
    IRRSourceSerializer,
    PeerASNSerializer,
    PeeringConnectionSerializer,
    PeeringFabricSerializer,
    PeeringFabricTypeSerializer,
    PeeringNetworkSerializer,
    PeeringSessionSerializer,
    RelationshipSerializer,
    RenderConfigRequestSerializer,
)


class RootView(APIRootView):
    def get_view_name(self):
        return "Peering Manager"


class RelationshipViewSet(NetBoxModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    filterset_class = RelationshipFilterSet


class IRRSourceViewSet(NetBoxModelViewSet):
    queryset = IRRSource.objects.all()
    serializer_class = IRRSourceSerializer
    filterset_class = IRRSourceFilterSet


class IRRPrefixListConfigViewSet(NetBoxModelViewSet):
    queryset = IRRPrefixListConfig.objects.select_related("prefix_list", "irr_source").prefetch_related("tags")
    serializer_class = IRRPrefixListConfigSerializer
    filterset_class = IRRPrefixListConfigFilterSet


class PeerASNViewSet(NetBoxModelViewSet):
    queryset = PeerASN.objects.select_related("asn")
    serializer_class = PeerASNSerializer
    filterset_class = PeerASNFilterSet


class PeeringSessionViewSet(NetBoxModelViewSet):
    queryset = PeeringSession.objects.select_related(
        "bgp_peer",
        "relationship",
        "peering_network",
    ).prefetch_related("tags")
    serializer_class = PeeringSessionSerializer
    filterset_class = PeeringSessionFilterSet


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
    permission_classes = [IsAuthenticated]

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
            response.data["session_count"] = len(context.get("sessions", []))

        return response
