import strawberry
import strawberry_django

from .types import (
    ASPathListRuleType,
    ASPathListType,
    BGPPeerGroupType,
    BGPSessionType,
    CommunityListRuleType,
    CommunityListType,
    CommunityType,
    PrefixListRuleType,
    PrefixListType,
    RoutingPolicyRuleType,
    RoutingPolicyType,
)


@strawberry.type(name="Query")
class NetBoxBGPQuery:
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
