from typing import Annotated

import strawberry
import strawberry_django
from dcim.graphql.filters import DeviceFilter
from ipam.graphql.filters import ASNFilter, IPAddressFilter
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry.scalars import ID
from strawberry_django import FilterLookup
from tenancy.graphql.filter_mixins import TenancyFilterMixin

from netbox_peering_manager.graphql.enums import (
    NetBoxBGPActionEnum,
    NetBoxBGPCommunityStatusEnum,
    NetBoxBGPIPAddressFamilyEnum,
    NetBoxBGPSessionStatusEnum,
)
from netbox_peering_manager.models import (
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
    PrefixList,
    PrefixListRule,
    RoutingPolicy,
    RoutingPolicyRule,
)

__all__ = (
    "NetBoxBGPCommunityFilter",
    "NetBoxBGPSessionFilter",
    "NetBoxBGPBGPPeerGroupFilter",
    "NetBoxBGPRoutingPolicyFilter",
    "NetBoxBGPRoutingPolicyRuleFilter",
    "NetBoxBGPPrefixListFilter",
    "NetBoxBGPPrefixListRuleFilter",
    "NetBoxBGPCommunityListFilter",
    "NetBoxBGPCommunityListRuleFilter",
    "NetBoxBGPASPathListFilter",
    "NetBoxBGPASPathListRuleFilter",
)


@strawberry_django.filter_type(ASPathList, lookups=True)
class NetBoxBGPASPathListFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(ASPathListRule, lookups=True)
class NetBoxBGPASPathListRuleFilter(NetBoxModelFilterMixin):
    value: FilterLookup[str] | None = strawberry_django.filter_field()
    aspath_list: (
        Annotated["NetBoxBGPASPathListFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aspath_list_id: ID | None = strawberry_django.filter_field()
    action: Annotated["NetBoxBGPActionEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(Community, lookups=True)
class NetBoxBGPCommunityFilter(TenancyFilterMixin, NetBoxModelFilterMixin):
    value: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    status: (
        Annotated["NetBoxBGPCommunityStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(BGPSession, lookups=True)
class NetBoxBGPSessionFilter(TenancyFilterMixin, NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated["NetBoxBGPSessionStatusEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )

    remote_as: Annotated["ASNFilter", strawberry.lazy("ipam.graphql.filters")] | None = strawberry_django.filter_field()
    remote_as_id: ID | None = strawberry_django.filter_field()

    local_as: Annotated["ASNFilter", strawberry.lazy("ipam.graphql.filters")] | None = strawberry_django.filter_field()
    local_as_id: ID | None = strawberry_django.filter_field()

    local_address: Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    local_address_id: ID | None = strawberry_django.filter_field()

    remote_address: Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    remote_address_id: ID | None = strawberry_django.filter_field()

    device: Annotated["DeviceFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()

    peer_group: (
        Annotated["NetBoxBGPBGPPeerGroupFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()

    import_policies: (
        Annotated["NetBoxBGPRoutingPolicyFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()

    export_policies: (
        Annotated["NetBoxBGPRoutingPolicyFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(BGPPeerGroup, lookups=True)
class NetBoxBGPBGPPeerGroupFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(RoutingPolicy, lookups=True)
class NetBoxBGPRoutingPolicyFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(RoutingPolicyRule, lookups=True)
class NetBoxBGPRoutingPolicyRuleFilter(NetBoxModelFilterMixin):
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    routing_policy: (
        Annotated["NetBoxBGPRoutingPolicyFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    routing_policy_id: ID | None = strawberry_django.filter_field()
    action: Annotated["NetBoxBGPActionEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    aspath_list: (
        Annotated["NetBoxBGPASPathListFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aspath_list_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(PrefixList, lookups=True)
class NetBoxBGPPrefixListFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    family: (
        Annotated["NetBoxBGPIPAddressFamilyEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(PrefixListRule, lookups=True)
class NetBoxBGPPrefixListRuleFilter(NetBoxModelFilterMixin):
    action: Annotated["NetBoxBGPActionEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    prefix_list: (
        Annotated["NetBoxBGPPrefixListFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    prefix_list_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(CommunityList, lookups=True)
class NetBoxBGPCommunityListFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(CommunityListRule, lookups=True)
class NetBoxBGPCommunityListRuleFilter(NetBoxModelFilterMixin):
    action: Annotated["NetBoxBGPActionEnum", strawberry.lazy("netbox_peering_manager.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )

    community_list: (
        Annotated["NetBoxBGPCommunityListFilter", strawberry.lazy("netbox_peering_manager.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    community_list_id: ID | None = strawberry_django.filter_field()
