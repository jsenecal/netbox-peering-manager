import strawberry
import strawberry_django

from .types import (
    ASPathListRuleType,
    ASPathListType,
    BFDType,
    BGPPeerGroupType,
    BGPSessionType,
    CommunityListRuleType,
    CommunityListType,
    CommunityType,
    PeeringConnectionGraphQLType,
    PeeringFabricGraphQLType,
    PeeringFabricTypeType,
    PeeringNetworkGraphQLType,
    PrefixListRuleType,
    PrefixListType,
    RelationshipType,
    RoutingPolicyRuleType,
    RoutingPolicyType,
)


@strawberry.type(name="Query")
class NetBoxBGPQuery:
    netbox_peering_manager_relationship: RelationshipType = strawberry_django.field()
    netbox_peering_manager_relationship_list: list[RelationshipType] = strawberry_django.field()

    netbox_peering_manager_bfd: BFDType = strawberry_django.field()
    netbox_peering_manager_bfd_list: list[BFDType] = strawberry_django.field()

    netbox_peering_manager_community: CommunityType = strawberry_django.field()
    netbox_peering_manager_community_list: list[CommunityType] = strawberry_django.field()

    netbox_peering_manager_session: BGPSessionType = strawberry_django.field()
    netbox_peering_manager_session_list: list[BGPSessionType] = strawberry_django.field()

    netbox_peering_manager_peer_group: BGPPeerGroupType = strawberry_django.field()
    netbox_peering_manager_peer_group_list: list[BGPPeerGroupType] = strawberry_django.field()

    netbox_peering_manager_routing_policy: RoutingPolicyType = strawberry_django.field()
    netbox_peering_manager_routing_policy_list: list[RoutingPolicyType] = strawberry_django.field()

    netbox_peering_manager_routing_policy_rule: RoutingPolicyRuleType = strawberry_django.field()
    netbox_peering_manager_routing_policy_rule_list: list[RoutingPolicyRuleType] = strawberry_django.field()

    netbox_peering_manager_prefixlist: PrefixListType = strawberry_django.field()
    netbox_peering_manager_prefixlist_list: list[PrefixListType] = strawberry_django.field()

    netbox_peering_manager_prefixlist_rule: PrefixListRuleType = strawberry_django.field()
    netbox_peering_manager_prefixlist_rule_list: list[PrefixListRuleType] = strawberry_django.field()

    netbox_peering_manager_communitylist: CommunityListType = strawberry_django.field()
    netbox_peering_manager_communitylist_list: list[CommunityListType] = strawberry_django.field()

    netbox_peering_manager_communitylist_rule: CommunityListRuleType = strawberry_django.field()
    netbox_peering_manager_communitylist_rule_list: list[CommunityListRuleType] = strawberry_django.field()

    netbox_peering_manager_aspathlist: ASPathListType = strawberry_django.field()
    netbox_peering_manager_aspathlist_list: list[ASPathListType] = strawberry_django.field()

    netbox_peering_manager_aspathlist_rule: ASPathListRuleType = strawberry_django.field()
    netbox_peering_manager_aspathlist_rule_list: list[ASPathListRuleType] = strawberry_django.field()

    # Peering Fabric queries
    netbox_peering_manager_peering_fabric_type: PeeringFabricTypeType = strawberry_django.field()
    netbox_peering_manager_peering_fabric_type_list: list[PeeringFabricTypeType] = strawberry_django.field()

    netbox_peering_manager_peering_fabric: PeeringFabricGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_fabric_list: list[PeeringFabricGraphQLType] = strawberry_django.field()

    netbox_peering_manager_peering_network: PeeringNetworkGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_network_list: list[PeeringNetworkGraphQLType] = strawberry_django.field()

    netbox_peering_manager_peering_connection: PeeringConnectionGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_connection_list: list[PeeringConnectionGraphQLType] = strawberry_django.field()
