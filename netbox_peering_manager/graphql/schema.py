import strawberry
import strawberry_django

from .types import (
    IRRPrefixListConfigType,
    IRRSourceType,
    PeerASNType,
    PeeringConnectionGraphQLType,
    PeeringFabricGraphQLType,
    PeeringFabricTypeType,
    PeeringNetworkGraphQLType,
    PeeringSessionType,
    RelationshipType,
)


@strawberry.type(name="Query")
class NetBoxBGPQuery:
    netbox_peering_manager_relationship: RelationshipType = strawberry_django.field()
    netbox_peering_manager_relationship_list: list[RelationshipType] = strawberry_django.field()

    netbox_peering_manager_irr_source: IRRSourceType = strawberry_django.field()
    netbox_peering_manager_irr_source_list: list[IRRSourceType] = strawberry_django.field()

    netbox_peering_manager_irr_prefix_list_config: IRRPrefixListConfigType = strawberry_django.field()
    netbox_peering_manager_irr_prefix_list_config_list: list[IRRPrefixListConfigType] = strawberry_django.field()

    netbox_peering_manager_peer_asn: PeerASNType = strawberry_django.field()
    netbox_peering_manager_peer_asn_list: list[PeerASNType] = strawberry_django.field()

    netbox_peering_manager_peering_session: PeeringSessionType = strawberry_django.field()
    netbox_peering_manager_peering_session_list: list[PeeringSessionType] = strawberry_django.field()

    # Peering Fabric queries
    netbox_peering_manager_peering_fabric_type: PeeringFabricTypeType = strawberry_django.field()
    netbox_peering_manager_peering_fabric_type_list: list[PeeringFabricTypeType] = strawberry_django.field()

    netbox_peering_manager_peering_fabric: PeeringFabricGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_fabric_list: list[PeeringFabricGraphQLType] = strawberry_django.field()

    netbox_peering_manager_peering_network: PeeringNetworkGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_network_list: list[PeeringNetworkGraphQLType] = strawberry_django.field()

    netbox_peering_manager_peering_connection: PeeringConnectionGraphQLType = strawberry_django.field()
    netbox_peering_manager_peering_connection_list: list[PeeringConnectionGraphQLType] = strawberry_django.field()
