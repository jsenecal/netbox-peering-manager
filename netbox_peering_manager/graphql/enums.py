import strawberry

from netbox_peering_manager.choices import PeeringStatusChoices

__all__ = ("PeeringStatusEnum",)

PeeringStatusEnum = strawberry.enum(PeeringStatusChoices.as_enum(), name="PeeringStatusEnum")
