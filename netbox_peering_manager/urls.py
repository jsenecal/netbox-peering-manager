from django.urls import include, path
from utilities.urls import get_model_urls

from . import views

app_name = "netbox_peering_manager"

urlpatterns = (
    # Relationships
    path(
        "relationship/",
        include(get_model_urls("netbox_peering_manager", "relationship", detail=False)),
    ),
    path(
        "relationship/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "relationship")),
    ),
    # BFD Profiles
    path(
        "bfd/",
        include(get_model_urls("netbox_peering_manager", "bfd", detail=False)),
    ),
    path(
        "bfd/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "bfd")),
    ),
    # IRR Sources
    path(
        "irr-source/",
        include(get_model_urls("netbox_peering_manager", "irrsource", detail=False)),
    ),
    path(
        "irr-source/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "irrsource")),
    ),
    # AS Path Lists
    path(
        "aspath-list/",
        include(get_model_urls("netbox_peering_manager", "aspathlist", detail=False)),
    ),
    path(
        "aspath-list/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "aspathlist")),
    ),
    # AS Path List Rules
    path(
        "aspath-list-rule/",
        include(get_model_urls("netbox_peering_manager", "aspathlistrule", detail=False)),
    ),
    path(
        "aspath-list-rule/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "aspathlistrule")),
    ),
    # Community
    path(
        "community/",
        include(get_model_urls("netbox_peering_manager", "community", detail=False)),
    ),
    path(
        "community/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "community")),
    ),
    # Community Lists
    path(
        "community-list/",
        include(get_model_urls("netbox_peering_manager", "communitylist", detail=False)),
    ),
    path(
        "community-list/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "communitylist")),
    ),
    # Community List Rules
    path(
        "community-list-rule/",
        include(get_model_urls("netbox_peering_manager", "communitylistrule", detail=False)),
    ),
    path(
        "community-list-rule/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "communitylistrule")),
    ),
    # Sessions
    path(
        "session/",
        include(get_model_urls("netbox_peering_manager", "bgpsession", detail=False)),
    ),
    path(
        "session/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "bgpsession")),
    ),
    # Peer ASNs
    path(
        "peer-asn/",
        include(get_model_urls("netbox_peering_manager", "peerasn", detail=False)),
    ),
    path(
        "peer-asn/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peerasn")),
    ),
    # Routing Policies
    path(
        "routing-policy/",
        include(get_model_urls("netbox_peering_manager", "routingpolicy", detail=False)),
    ),
    path(
        "routing-policy/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "routingpolicy")),
    ),
    # Routing Policy Rules
    path(
        "routing-policy-rule/",
        include(get_model_urls("netbox_peering_manager", "routingpolicyrule", detail=False)),
    ),
    path(
        "routing-policy-rule/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "routingpolicyrule")),
    ),
    # Peer Groups
    path(
        "peer-group/",
        include(get_model_urls("netbox_peering_manager", "bgppeergroup", detail=False)),
    ),
    path(
        "peer-group/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "bgppeergroup")),
    ),
    # Prefix Lists
    path(
        "prefix-list/",
        include(get_model_urls("netbox_peering_manager", "prefixlist", detail=False)),
    ),
    path(
        "prefix-list/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "prefixlist")),
    ),
    # Prefix List Rules
    path(
        "prefix-list-rule/",
        include(get_model_urls("netbox_peering_manager", "prefixlistrule", detail=False)),
    ),
    path(
        "prefix-list-rule/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "prefixlistrule")),
    ),
    # Peering Fabric Types
    path(
        "peering-fabric-type/",
        include(get_model_urls("netbox_peering_manager", "peeringfabrictype", detail=False)),
    ),
    path(
        "peering-fabric-type/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peeringfabrictype")),
    ),
    # Peering Fabrics
    path(
        "peering-fabric/",
        include(get_model_urls("netbox_peering_manager", "peeringfabric", detail=False)),
    ),
    path(
        "peering-fabric/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peeringfabric")),
    ),
    # Peering Networks
    path(
        "peering-network/",
        include(get_model_urls("netbox_peering_manager", "peeringnetwork", detail=False)),
    ),
    path(
        "peering-network/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peeringnetwork")),
    ),
    # Peering Connections
    path(
        "peering-connection/",
        include(get_model_urls("netbox_peering_manager", "peeringconnection", detail=False)),
    ),
    path(
        "peering-connection/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peeringconnection")),
    ),
    # PeeringDB Integration
    path(
        "peeringdb/search/",
        views.PeeringDBIXSearchView.as_view(),
        name="peeringdb_ix_search",
    ),
    path(
        "peering-fabric/create-from-peeringdb/",
        views.PeeringFabricCreateFromPeeringDBView.as_view(),
        name="peeringfabric_create_from_peeringdb",
    ),
    path(
        "peering-fabric/<int:pk>/sync-peeringdb/",
        views.PeeringFabricSyncPeeringDBView.as_view(),
        name="peeringfabric_sync_peeringdb",
    ),
    path(
        "peering-fabric/<int:pk>/create-session-from-peer/<int:peer_pk>/",
        views.CreateSessionFromPeerView.as_view(),
        name="peeringfabric_create_session_from_peer",
    ),
)
