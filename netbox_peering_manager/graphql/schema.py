from typing import List

import strawberry
import strawberry_django

from netbox_peering_manager.models import (
    Community,
    BGPSession,
    RoutingPolicy,
    BGPPeerGroup,
    RoutingPolicyRule,
    PrefixList,
    PrefixListRule,
    CommunityList,
    CommunityListRule,
    ASPathList,
    ASPathListRule
)
from .types import (
    CommunityType,
    BGPSessionType,
    BGPPeerGroupType,
    RoutingPolicyType,
    RoutingPolicyRuleType,
    PrefixListType,
    PrefixListRuleType,
    CommunityListType,
    CommunityListRuleType,
    ASPathListType,
    ASPathListRuleType
)


@strawberry.type(name="Query")
class NetBoxBGPQuery:

    netbox_peering_manager_community: CommunityType = strawberry_django.field()
    netbox_peering_manager_community_list: List[CommunityType] = strawberry_django.field()

    netbox_peering_manager_session: BGPSessionType = strawberry_django.field()
    netbox_peering_manager_session_list: List[BGPSessionType] = strawberry_django.field()

    netbox_peering_manager_peer_group: BGPPeerGroupType = strawberry_django.field()
    netbox_peering_manager_peer_group_list: List[BGPPeerGroupType] = strawberry_django.field()

    netbox_peering_manager_routing_policy: RoutingPolicyType = strawberry_django.field()
    netbox_peering_manager_routing_policy_list: List[RoutingPolicyType] = strawberry_django.field()

    netbox_peering_manager_routing_policy_rule: RoutingPolicyRuleType = strawberry_django.field()
    netbox_peering_manager_routing_policy_rule_list: List[RoutingPolicyRuleType] = strawberry_django.field()

    netbox_peering_manager_prefixlist: PrefixListType = strawberry_django.field()
    netbox_peering_manager_prefixlist_list: List[PrefixListType] = strawberry_django.field()

    netbox_peering_manager_prefixlist_rule: PrefixListRuleType = strawberry_django.field()
    netbox_peering_manager_prefixlist_rule_list: List[PrefixListRuleType] = strawberry_django.field()

    netbox_peering_manager_communitylist: CommunityListType = strawberry_django.field()
    netbox_peering_manager_communitylist_list: List[CommunityListType] = strawberry_django.field()

    netbox_peering_manager_communitylist_rule: CommunityListRuleType = strawberry_django.field()
    netbox_peering_manager_communitylist_rule_list: List[CommunityListRuleType] = strawberry_django.field()

    netbox_peering_manager_aspathlist: ASPathListType = strawberry_django.field()
    netbox_peering_manager_aspathlist_list: List[ASPathListType] = strawberry_django.field()

    netbox_peering_manager_aspathlist_rule: ASPathListRuleType = strawberry_django.field()
    netbox_peering_manager_aspathlist_rule_list: List[ASPathListRuleType] = strawberry_django.field()