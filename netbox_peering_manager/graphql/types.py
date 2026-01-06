from typing import Annotated

import strawberry
import strawberry_django
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import NetBoxObjectType

from netbox_peering_manager.models import (
    BFD,
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
    IRRSource,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PrefixList,
    PrefixListRule,
    Relationship,
    RoutingPolicy,
    RoutingPolicyRule,
)

from .filters import (
    NetBoxBGPASPathListFilter,
    NetBoxBGPASPathListRuleFilter,
    NetBoxBGPBFDFilter,
    NetBoxBGPBGPPeerGroupFilter,
    NetBoxBGPCommunityFilter,
    NetBoxBGPCommunityListFilter,
    NetBoxBGPCommunityListRuleFilter,
    NetBoxBGPIRRSourceFilter,
    NetBoxBGPPeeringConnectionFilter,
    NetBoxBGPPeeringFabricFilter,
    NetBoxBGPPeeringFabricTypeFilter,
    NetBoxBGPPeeringNetworkFilter,
    NetBoxBGPPrefixListFilter,
    NetBoxBGPPrefixListRuleFilter,
    NetBoxBGPRelationshipFilter,
    NetBoxBGPRoutingPolicyFilter,
    NetBoxBGPRoutingPolicyRuleFilter,
    NetBoxBGPSessionFilter,
)


@strawberry_django.type(Relationship, fields="__all__", filters=NetBoxBGPRelationshipFilter)
class RelationshipType(NetBoxObjectType):
    name: str
    slug: str
    description: str
    color: str
    sessions: list[Annotated["BGPSessionType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(BFD, fields="__all__", filters=NetBoxBGPBFDFilter)
class BFDType(NetBoxObjectType):
    name: str
    description: str
    minimum_transmit_interval: int
    minimum_receive_interval: int
    detect_multiplier: int
    hold_time: int | None
    sessions: list[Annotated["BGPSessionType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


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
    prefix_lists: list[Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(ASPathList, fields="__all__", filters=NetBoxBGPASPathListFilter)
class ASPathListType(NetBoxObjectType):
    name: str
    description: str
    rules: list[Annotated["ASPathListRuleType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(ASPathListRule, fields="__all__", filters=NetBoxBGPASPathListRuleFilter)
class ASPathListRuleType(NetBoxObjectType):
    aspath_list: Annotated["ASPathListType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    index: BigInt
    action: str
    pattern: str
    description: str


@strawberry_django.type(Community, fields="__all__", filters=NetBoxBGPCommunityFilter)
class CommunityType(NetBoxObjectType):
    site: Annotated["SiteType", strawberry.lazy("dcim.graphql.types")] | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    status: str
    role: Annotated["RoleType", strawberry.lazy("ipam.graphql.types")] | None
    description: str


@strawberry_django.type(BGPSession, fields="__all__", filters=NetBoxBGPSessionFilter)
class BGPSessionType(NetBoxObjectType):
    name: str
    site: Annotated["SiteType", strawberry.lazy("dcim.graphql.types")] | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    device: Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")] | None
    virtualmachine: Annotated["VirtualMachineType", strawberry.lazy("virtualization.graphql.types")] | None
    local_address: Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
    remote_address: Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
    local_as: Annotated["ASNType", strawberry.lazy("ipam.graphql.types")]
    remote_as: Annotated["ASNType", strawberry.lazy("ipam.graphql.types")]
    status: str
    enabled: bool
    description: str
    peer_group: Annotated["BGPPeerGroupType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    relationship: Annotated["RelationshipType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    bfd: Annotated["BFDType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    multihop_ttl: int
    service_reference: str
    import_policies: list[Annotated["RoutingPolicyType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    export_policies: list[Annotated["RoutingPolicyType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    prefix_list_in: Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    prefix_list_out: Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    peering_network: (
        Annotated["PeeringNetworkGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    )


@strawberry_django.type(BGPPeerGroup, fields="__all__", filters=NetBoxBGPBGPPeerGroupFilter)
class BGPPeerGroupType(NetBoxObjectType):
    name: str
    description: str
    import_policies: list[Annotated["RoutingPolicyType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    export_policies: list[Annotated["RoutingPolicyType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(RoutingPolicy, fields="__all__", filters=NetBoxBGPRoutingPolicyFilter)
class RoutingPolicyType(NetBoxObjectType):
    name: str
    description: str
    rules: list[Annotated["RoutingPolicyRuleType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(RoutingPolicyRule, fields="__all__", filters=NetBoxBGPRoutingPolicyRuleFilter)
class RoutingPolicyRuleType(NetBoxObjectType):
    routing_policy: Annotated["RoutingPolicyType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    index: BigInt
    action: str
    description: str
    continue_entry: BigInt | None
    match_community: list[Annotated["CommunityType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    match_community_list: list[Annotated["CommunityListType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    match_ip_address: list[Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
    match_ipv6_address: list[Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(PrefixList, fields="__all__", filters=NetBoxBGPPrefixListFilter)
class PrefixListType(NetBoxObjectType):
    name: str
    description: str
    family: str
    source_as_set: str
    irr_source: Annotated["IRRSourceType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    prefrules: list[Annotated["PrefixListRuleType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(PrefixListRule, fields="__all__", filters=NetBoxBGPPrefixListRuleFilter)
class PrefixListRuleType(NetBoxObjectType):
    prefix_list: Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    index: BigInt
    action: str
    prefix: Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")] | None
    prefix_custom: str | None
    ge: BigInt
    le: BigInt
    description: str


@strawberry_django.type(CommunityList, fields="__all__", filters=NetBoxBGPCommunityListFilter)
class CommunityListType(NetBoxObjectType):
    name: str
    description: str
    commlistrules: list[Annotated["CommunityListRuleType", strawberry.lazy("netbox_peering_manager.graphql.types")]]


@strawberry_django.type(CommunityListRule, fields="__all__", filters=NetBoxBGPCommunityListRuleFilter)
class CommunityListRuleType(NetBoxObjectType):
    community_list: Annotated["CommunityListType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    action: str
    community: Annotated["CommunityType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    description: str


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
    peer_group: Annotated["BGPPeerGroupType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
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


@strawberry_django.type(PeeringConnection, fields="__all__", filters=NetBoxBGPPeeringConnectionFilter)
class PeeringConnectionGraphQLType(NetBoxObjectType):
    description: str
    status: str
    peering_network: Annotated["PeeringNetworkGraphQLType", strawberry.lazy("netbox_peering_manager.graphql.types")]
    interface: Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")]
