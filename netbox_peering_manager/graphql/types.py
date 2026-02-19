from typing import Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

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

from .filters import (
    NetBoxBGPIRRPrefixListConfigFilter,
    NetBoxBGPIRRSourceFilter,
    NetBoxBGPPeerASNFilter,
    NetBoxBGPPeeringConnectionFilter,
    NetBoxBGPPeeringFabricFilter,
    NetBoxBGPPeeringFabricTypeFilter,
    NetBoxBGPPeeringNetworkFilter,
    NetBoxBGPPeeringSessionFilter,
    NetBoxBGPRelationshipFilter,
)


@strawberry_django.type(Relationship, fields="__all__", filters=NetBoxBGPRelationshipFilter)
class RelationshipType(NetBoxObjectType):
    name: str
    slug: str
    description: str
    color: str
    peering_sessions: list[Annotated["PeeringSessionType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(IRRSource, fields="__all__", filters=NetBoxBGPIRRSourceFilter)
class IRRSourceType(NetBoxObjectType):
    name: str
    slug: str
    url: str
    sources: str
    cache_ttl: int | None
    sync_interval: int
    enabled: bool
    description: str
    irr_prefix_list_configs: list[
        Annotated["IRRPrefixListConfigType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    ]


@strawberry_django.type(IRRPrefixListConfig, fields="__all__", filters=NetBoxBGPIRRPrefixListConfigFilter)
class IRRPrefixListConfigType(NetBoxObjectType):
    prefix_list: Annotated["PrefixListType", strawberry.lazy("netbox_routing.graphql.types")]
    irr_source: Annotated["IRRSourceType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    source_as_set: str
    sync_interval: int


@strawberry_django.type(PeerASN, fields="__all__", filters=NetBoxBGPPeerASNFilter)
class PeerASNType(NetBoxObjectType):
    asn: Annotated["ASNType", strawberry.lazy("ipam.graphql.types")]
    affiliated: bool
    irr_as_set: str
    ipv4_max_prefixes: int | None
    ipv6_max_prefixes: int | None
    peeringdb_id: int | None


@strawberry_django.type(PeeringSession, fields="__all__", filters=NetBoxBGPPeeringSessionFilter)
class PeeringSessionType(NetBoxObjectType):
    bgp_peer: Annotated["BGPPeerType", strawberry.lazy("netbox_routing.graphql.types")]
    relationship: Annotated["RelationshipType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    peering_network: (
        Annotated["PeeringNetworkGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    )
    service_reference: str


# =============================================================================
# Peering Fabric Types
# =============================================================================


@strawberry_django.type(PeeringFabricType, fields="__all__", filters=NetBoxBGPPeeringFabricTypeFilter)
class PeeringFabricTypeType(NetBoxObjectType):
    name: str
    slug: str
    description: str
    color: str
    fabrics: list[Annotated["PeeringFabricGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(PeeringFabric, fields="__all__", filters=NetBoxBGPPeeringFabricFilter)
class PeeringFabricGraphQLType(NetBoxObjectType):
    name: str
    slug: str
    description: str
    status: str
    type: Annotated["PeeringFabricTypeType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    site: Annotated["SiteType", strawberry.lazy("dcim.graphql.types")] | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    networks: list[Annotated["PeeringNetworkGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(PeeringNetwork, fields="__all__", filters=NetBoxBGPPeeringNetworkFilter)
class PeeringNetworkGraphQLType(NetBoxObjectType):
    name: str
    description: str
    status: str
    fabric: Annotated["PeeringFabricGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")]
    vlan: Annotated["VLANType", strawberry.lazy("ipam.graphql.types")] | None
    connections: list[
        Annotated["PeeringConnectionGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    ]
    peering_sessions: list[Annotated["PeeringSessionType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(PeeringConnection, fields="__all__", filters=NetBoxBGPPeeringConnectionFilter)
class PeeringConnectionGraphQLType(NetBoxObjectType):
    description: str
    status: str
    peering_network: Annotated["PeeringNetworkGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    interface: Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")]
