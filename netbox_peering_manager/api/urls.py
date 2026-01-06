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
    PeeringConnectionViewSet,
    PeeringFabricTypeViewSet,
    PeeringFabricViewSet,
    PeeringNetworkViewSet,
    PrefixListRuleViewSet,
    PrefixListViewSet,
    RelationshipViewSet,
    RootView,
    RoutingPolicyRuleViewSet,
    RoutingPolicyViewSet,
)

router = NetBoxRouter()
router.APIRootView = RootView
router.register("relationship", RelationshipViewSet)
router.register("bfd", BFDViewSet)
router.register("irr-source", IRRSourceViewSet)
router.register("session", BGPSessionViewSet, "session")
router.register("bgpsession", BGPSessionViewSet, "bgpsession")
router.register("routing-policy", RoutingPolicyViewSet)
router.register("routing-policy-rule", RoutingPolicyRuleViewSet)
router.register("peer-group", BGPPeerGroupViewSet, "peergroup")
router.register("bgppeergroup", BGPPeerGroupViewSet, "bgppeergroup")
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

urlpatterns = router.urls
