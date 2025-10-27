import strawberry

from netbox_peering_manager.choices import (
    ActionChoices,
    CommunityStatusChoices,
    IPAddressFamilyChoices,
    SessionStatusChoices,
)

__all__ = (
    "NetBoxBGPCommunityStatusEnum",
    "NetBoxBGPSessionStatusEnum",
    "NetBoxBGPActionEnum",
    "NetBoxBGPIPAddressFamilyEnum",
)

NetBoxBGPCommunityStatusEnum = strawberry.enum(CommunityStatusChoices.as_enum(), name="NetBoxBGPCommunityStatusEnum")
NetBoxBGPSessionStatusEnum = strawberry.enum(SessionStatusChoices.as_enum(), name="NetBoxBGPSessionStatusEnum")
NetBoxBGPActionEnum = strawberry.enum(ActionChoices.as_enum(), name="NetBoxBGPActionEnum")
NetBoxBGPIPAddressFamilyEnum = strawberry.enum(IPAddressFamilyChoices.as_enum(), name="NetBoxBGPIPAddressFamilyEnum")
