from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from .views import (
    ASPathListRuleViewSet,
    ASPathListViewSet,
    BFDViewSet,
    BGPPeerGroupViewSet,
    BGPSessionViewSet,
    CommunityListRuleViewSet,
    CommunityListViewSet,
    CommunityViewSet,
    IRRSourceViewSet,
    PeerASNViewSet,
    PeeringConnectionViewSet,
    PeeringFabricTypeViewSet,
    PeeringFabricViewSet,
    PeeringNetworkViewSet,
    PrefixListRuleViewSet,
    PrefixListViewSet,
    RelationshipViewSet,
    RenderConfigView,
    RootView,
    RoutingPolicyRuleViewSet,
    RoutingPolicyViewSet,
)

router = NetBoxRouter()
router.APIRootView = RootView
router.register("relationship", RelationshipViewSet)
router.register("bfd", BFDViewSet)
router.register("irr-source", IRRSourceViewSet)
router.register("peer-asn", PeerASNViewSet)
router.register("bgpsession", BGPSessionViewSet)
router.register("routing-policy", RoutingPolicyViewSet)
router.register("routing-policy-rule", RoutingPolicyRuleViewSet)
router.register("bgppeergroup", BGPPeerGroupViewSet)
router.register("community", CommunityViewSet)
router.register("prefix-list", PrefixListViewSet)
router.register("prefix-list-rule", PrefixListRuleViewSet)
router.register("community-list", CommunityListViewSet)
router.register("community-list-rule", CommunityListRuleViewSet)
router.register("aspath-list", ASPathListViewSet)
router.register("aspath-list-rule", ASPathListRuleViewSet)

# Peering Fabric routes
router.register("peering-fabric-type", PeeringFabricTypeViewSet)
router.register("peering-fabric", PeeringFabricViewSet)
router.register("peering-network", PeeringNetworkViewSet)
router.register("peering-connection", PeeringConnectionViewSet)

urlpatterns = [
    path("render-config/", RenderConfigView.as_view(), name="render_config"),
    path("", include(router.urls)),
]
