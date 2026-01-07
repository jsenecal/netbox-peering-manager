import strawberry
from ipam.choices import IPAddressFamilyChoices

from netbox_peering_manager.choices import (
    ActionChoices,
    CommunityStatusChoices,
    PeeringStatusChoices,
    SessionStatusChoices,
)

__all__ = (
    "NetBoxBGPCommunityStatusEnum",
    "NetBoxBGPSessionStatusEnum",
    "NetBoxBGPActionEnum",
    "NetBoxBGPIPAddressFamilyEnum",
    "NetBoxBGPPeeringStatusEnum",
)

NetBoxBGPCommunityStatusEnum = strawberry.enum(CommunityStatusChoices.as_enum(), name="NetBoxBGPCommunityStatusEnum")
NetBoxBGPSessionStatusEnum = strawberry.enum(SessionStatusChoices.as_enum(), name="NetBoxBGPSessionStatusEnum")
NetBoxBGPActionEnum = strawberry.enum(ActionChoices.as_enum(), name="NetBoxBGPActionEnum")
NetBoxBGPIPAddressFamilyEnum = strawberry.enum(
    IPAddressFamilyChoices.as_enum(prefix="family"), name="NetBoxBGPIPAddressFamilyEnum"
)
NetBoxBGPPeeringStatusEnum = strawberry.enum(PeeringStatusChoices.as_enum(), name="NetBoxBGPPeeringStatusEnum")
