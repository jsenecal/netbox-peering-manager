import strawberry

from netbox_peering_manager.choices import PeeringStatusChoices

__all__ = ("NetBoxBGPPeeringStatusEnum",)

NetBoxBGPPeeringStatusEnum = strawberry.enum(PeeringStatusChoices.as_enum(), name="NetBoxBGPPeeringStatusEnum")
