from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from .views import (
    IRRPrefixListConfigViewSet,
    IRRSourceViewSet,
    PeerASNViewSet,
    PeeringConnectionViewSet,
    PeeringFabricTypeViewSet,
    PeeringFabricViewSet,
    PeeringNetworkViewSet,
    PeeringSessionViewSet,
    RelationshipViewSet,
    RenderConfigView,
    RootView,
)

router = NetBoxRouter()
router.APIRootView = RootView
router.register("relationship", RelationshipViewSet)
router.register("irr-source", IRRSourceViewSet)
router.register("irr-prefix-list-config", IRRPrefixListConfigViewSet)
router.register("peer-asn", PeerASNViewSet)
router.register("peering-session", PeeringSessionViewSet)

# Peering Fabric routes
router.register("peering-fabric-type", PeeringFabricTypeViewSet)
router.register("peering-fabric", PeeringFabricViewSet)
router.register("peering-network", PeeringNetworkViewSet)
router.register("peering-connection", PeeringConnectionViewSet)

urlpatterns = [
    path("render-config/", RenderConfigView.as_view(), name="render_config"),
    path("", include(router.urls)),
]
