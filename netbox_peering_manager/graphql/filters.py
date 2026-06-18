from typing import Annotated

import strawberry
import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter
from strawberry.scalars import ID
from strawberry_django import FilterLookup

try:
    from strawberry_django import StrFilterLookup
except ImportError:
    StrFilterLookup = FilterLookup[str]
from tenancy.graphql.filter_mixins import TenancyFilterMixin

from netbox_peering_manager.graphql.enums import NetBoxBGPPeeringStatusEnum
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

__all__ = (
    "NetBoxBGPRelationshipFilter",
    "NetBoxBGPIRRSourceFilter",
    "NetBoxBGPIRRPrefixListConfigFilter",
    "NetBoxBGPPeerASNFilter",
    "NetBoxBGPPeeringSessionFilter",
    "NetBoxBGPPeeringFabricTypeFilter",
    "NetBoxBGPPeeringFabricFilter",
    "NetBoxBGPPeeringNetworkFilter",
    "NetBoxBGPPeeringConnectionFilter",
)


@strawberry_django.filter_type(Relationship, lookups=True)
class NetBoxBGPRelationshipFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()


@strawberry_django.filter_type(IRRSource, lookups=True)
class NetBoxBGPIRRSourceFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(IRRPrefixListConfig, lookups=True)
class NetBoxBGPIRRPrefixListConfigFilter(NetBoxModelFilter):
    source_as_set: StrFilterLookup | None = strawberry_django.filter_field()
    irr_source: (
        Annotated["NetBoxBGPIRRSourceFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    irr_source_id: ID | None = strawberry_django.filter_field()
    prefix_list_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeerASN, lookups=True)
class NetBoxBGPPeerASNFilter(NetBoxModelFilter):
    affiliated: FilterLookup[bool] | None = strawberry_django.filter_field()
    irr_as_set: StrFilterLookup | None = strawberry_django.filter_field()
    peeringdb_id: FilterLookup[int] | None = strawberry_django.filter_field()
    asn_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringSession, lookups=True)
class NetBoxBGPPeeringSessionFilter(NetBoxModelFilter):
    service_reference: StrFilterLookup | None = strawberry_django.filter_field()
    bgp_peer_id: ID | None = strawberry_django.filter_field()
    relationship: (
        Annotated["NetBoxBGPRelationshipFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    relationship_id: ID | None = strawberry_django.filter_field()
    peering_network: (
        Annotated["NetBoxBGPPeeringNetworkFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    peering_network_id: ID | None = strawberry_django.filter_field()


# =============================================================================
# Peering Fabric Filters
# =============================================================================


@strawberry_django.filter_type(PeeringFabricType, lookups=True)
class NetBoxBGPPeeringFabricTypeFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringFabric, lookups=True)
class NetBoxBGPPeeringFabricFilter(TenancyFilterMixin, NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["NetBoxBGPPeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    type: (
        Annotated["NetBoxBGPPeeringFabricTypeFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    type_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringNetwork, lookups=True)
class NetBoxBGPPeeringNetworkFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["NetBoxBGPPeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    fabric: (
        Annotated["NetBoxBGPPeeringFabricFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    fabric_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringConnection, lookups=True)
class NetBoxBGPPeeringConnectionFilter(NetBoxModelFilter):
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["NetBoxBGPPeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    peering_network: (
        Annotated["NetBoxBGPPeeringNetworkFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    peering_network_id: ID | None = strawberry_django.filter_field()
    interface_id: ID | None = strawberry_django.filter_field()


# NetBox 4.6+ auto-discovers a model's GraphQL filter at the conventional
# `<app>.graphql.filters.<Model>Filter` path. These plugin filters keep their
# historical `NetBoxBGP*` names (which also name the GraphQL schema input types,
# so renaming them would be a breaking schema change); expose conventional-name
# aliases so the canonical class is discoverable without altering the schema.
RelationshipFilter = NetBoxBGPRelationshipFilter
IRRSourceFilter = NetBoxBGPIRRSourceFilter
IRRPrefixListConfigFilter = NetBoxBGPIRRPrefixListConfigFilter
PeerASNFilter = NetBoxBGPPeerASNFilter
PeeringSessionFilter = NetBoxBGPPeeringSessionFilter
PeeringFabricTypeFilter = NetBoxBGPPeeringFabricTypeFilter
PeeringFabricFilter = NetBoxBGPPeeringFabricFilter
PeeringNetworkFilter = NetBoxBGPPeeringNetworkFilter
PeeringConnectionFilter = NetBoxBGPPeeringConnectionFilter
