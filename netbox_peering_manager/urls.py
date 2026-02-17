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
    # IRR Sources
    path(
        "irr-source/",
        include(get_model_urls("netbox_peering_manager", "irrsource", detail=False)),
    ),
    path(
        "irr-source/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "irrsource")),
    ),
    # IRR Prefix List Configs
    path(
        "irr-prefix-list-config/",
        include(get_model_urls("netbox_peering_manager", "irrprefixlistconfig", detail=False)),
    ),
    path(
        "irr-prefix-list-config/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "irrprefixlistconfig")),
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
    # Peering Sessions
    path(
        "peering-session/",
        include(get_model_urls("netbox_peering_manager", "peeringsession", detail=False)),
    ),
    path(
        "peering-session/<int:pk>/",
        include(get_model_urls("netbox_peering_manager", "peeringsession")),
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
)
