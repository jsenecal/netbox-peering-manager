from typing import Annotated

import strawberry
import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter
from strawberry.scalars import ID
from strawberry_django import FilterLookup, StrFilterLookup
from tenancy.graphql.filter_mixins import TenancyFilterMixin

from netbox_peering_manager.graphql.enums import PeeringStatusEnum
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
    "RelationshipFilter",
    "IRRSourceFilter",
    "IRRPrefixListConfigFilter",
    "PeerASNFilter",
    "PeeringSessionFilter",
    "PeeringFabricTypeFilter",
    "PeeringFabricFilter",
    "PeeringNetworkFilter",
    "PeeringConnectionFilter",
)


@strawberry_django.filter_type(Relationship, lookups=True)
class RelationshipFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()


@strawberry_django.filter_type(IRRSource, lookups=True)
class IRRSourceFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(IRRPrefixListConfig, lookups=True)
class IRRPrefixListConfigFilter(NetBoxModelFilter):
    source_as_set: StrFilterLookup | None = strawberry_django.filter_field()
    irr_source: Annotated["IRRSourceFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    irr_source_id: ID | None = strawberry_django.filter_field()
    prefix_list_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeerASN, lookups=True)
class PeerASNFilter(NetBoxModelFilter):
    affiliated: FilterLookup[bool] | None = strawberry_django.filter_field()
    irr_as_set: StrFilterLookup | None = strawberry_django.filter_field()
    peeringdb_id: FilterLookup[int] | None = strawberry_django.filter_field()
    asn_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringSession, lookups=True)
class PeeringSessionFilter(NetBoxModelFilter):
    service_reference: StrFilterLookup | None = strawberry_django.filter_field()
    bgp_peer_id: ID | None = strawberry_django.filter_field()
    relationship: Annotated["RelationshipFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    relationship_id: ID | None = strawberry_django.filter_field()
    peering_network: (
        Annotated["PeeringNetworkFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    peering_network_id: ID | None = strawberry_django.filter_field()


# =============================================================================
# Peering Fabric Filters
# =============================================================================


@strawberry_django.filter_type(PeeringFabricType, lookups=True)
class PeeringFabricTypeFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringFabric, lookups=True)
class PeeringFabricFilter(TenancyFilterMixin, NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["PeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    type: Annotated["PeeringFabricTypeFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringNetwork, lookups=True)
class PeeringNetworkFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["PeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    fabric: Annotated["PeeringFabricFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    fabric_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PeeringConnection, lookups=True)
class PeeringConnectionFilter(NetBoxModelFilter):
    description: StrFilterLookup | None = strawberry_django.filter_field()
    status: Annotated["PeeringStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    peering_network: (
        Annotated["PeeringNetworkFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    peering_network_id: ID | None = strawberry_django.filter_field()
    interface_id: ID | None = strawberry_django.filter_field()
