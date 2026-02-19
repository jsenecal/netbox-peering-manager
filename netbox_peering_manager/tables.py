import django_tables2 as tables
from netbox.tables import NetBoxTable
from netbox.tables.columns import BooleanColumn, ChoiceFieldColumn, ColorColumn, TagColumn

from .models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringDBPeer,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PeeringSession,
    Relationship,
)

# =============================================================================
# Relationship Table
# =============================================================================


class RelationshipTable(NetBoxTable):
    name = tables.LinkColumn()
    color = ColorColumn()
    tags = TagColumn(url_name="plugins:netbox_peering_manager:relationship_list")

    class Meta(NetBoxTable.Meta):
        model = Relationship
        fields = ("pk", "name", "slug", "color", "description", "tags", "actions")
        default_columns = ("pk", "name", "color", "description")


# =============================================================================
# IRRSource Table
# =============================================================================


class IRRSourceTable(NetBoxTable):
    name = tables.LinkColumn()
    enabled = BooleanColumn()
    sync_interval = tables.Column(verbose_name="Sync Interval (min)")
    prefix_list_count = tables.Column(verbose_name="Prefix Lists")
    tags = TagColumn(url_name="plugins:netbox_peering_manager:irrsource_list")

    class Meta(NetBoxTable.Meta):
        model = IRRSource
        fields = (
            "pk",
            "name",
            "slug",
            "url",
            "sources",
            "sync_interval",
            "enabled",
            "prefix_list_count",
            "description",
            "tags",
            "actions",
        )
        default_columns = ("pk", "name", "url", "enabled", "sync_interval", "prefix_list_count")


# =============================================================================
# IRRPrefixListConfig Table
# =============================================================================


class IRRPrefixListConfigTable(NetBoxTable):
    prefix_list = tables.Column(linkify=True, verbose_name="Prefix List")
    irr_source = tables.Column(linkify=True, verbose_name="IRR Source")
    source_as_set = tables.Column(verbose_name="AS-SET")
    sync_interval = tables.Column(verbose_name="Sync Interval (min)")
    tags = TagColumn(url_name="plugins:netbox_peering_manager:irrprefixlistconfig_list")

    class Meta(NetBoxTable.Meta):
        model = IRRPrefixListConfig
        fields = (
            "pk",
            "prefix_list",
            "irr_source",
            "source_as_set",
            "sync_interval",
            "tags",
            "actions",
        )
        default_columns = ("pk", "prefix_list", "irr_source", "source_as_set", "sync_interval")


# =============================================================================
# PeeringSession Table
# =============================================================================


class PeeringSessionTable(NetBoxTable):
    bgp_peer = tables.Column(linkify=True, verbose_name="BGP Peer")
    relationship = tables.Column(linkify=True)
    peering_network = tables.Column(linkify=True, verbose_name="Peering Network")
    service_reference = tables.Column(verbose_name="Service Ref")
    tags = TagColumn(url_name="plugins:netbox_peering_manager:peeringsession_list")

    class Meta(NetBoxTable.Meta):
        model = PeeringSession
        fields = (
            "pk",
            "bgp_peer",
            "relationship",
            "peering_network",
            "service_reference",
            "tags",
            "actions",
        )
        default_columns = ("pk", "bgp_peer", "relationship", "peering_network", "service_reference")


# =============================================================================
# PeerASN Table
# =============================================================================


class PeerASNTable(NetBoxTable):
    asn = tables.Column(linkify=True, verbose_name="ASN")
    affiliated = BooleanColumn()
    ipv4_max_prefixes = tables.Column(verbose_name="IPv4 Max Prefixes")
    ipv6_max_prefixes = tables.Column(verbose_name="IPv6 Max Prefixes")
    peeringdb_id = tables.Column(verbose_name="PeeringDB ID")
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = PeerASN
        fields = (
            "pk",
            "id",
            "asn",
            "affiliated",
            "irr_as_set",
            "ipv4_max_prefixes",
            "ipv6_max_prefixes",
            "peeringdb_id",
            "tags",
        )
        default_columns = (
            "asn",
            "affiliated",
            "irr_as_set",
            "ipv4_max_prefixes",
            "ipv6_max_prefixes",
        )


# =============================================================================
# Peering Fabric Tables
# =============================================================================


class PeeringFabricTypeTable(NetBoxTable):
    name = tables.LinkColumn()
    color = ColorColumn()
    tags = TagColumn(url_name="plugins:netbox_peering_manager:peeringfabrictype_list")
    fabric_count = tables.Column(verbose_name="Fabrics")

    class Meta(NetBoxTable.Meta):
        model = PeeringFabricType
        fields = ("pk", "name", "slug", "color", "description", "fabric_count", "tags", "actions")
        default_columns = ("pk", "name", "color", "fabric_count", "description")


class PeeringFabricTable(NetBoxTable):
    name = tables.LinkColumn()
    type = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    site = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)
    network_count = tables.Column(verbose_name="Networks")
    peeringdb_linked = BooleanColumn(
        accessor="peeringdb",
        verbose_name="PeeringDB",
    )
    tags = TagColumn(url_name="plugins:netbox_peering_manager:peeringfabric_list")

    class Meta(NetBoxTable.Meta):
        model = PeeringFabric
        fields = (
            "pk",
            "name",
            "slug",
            "type",
            "status",
            "site",
            "tenant",
            "network_count",
            "peeringdb_linked",
            "tags",
            "actions",
        )
        default_columns = ("pk", "name", "type", "status", "site", "network_count", "peeringdb_linked")


class PeeringNetworkTable(NetBoxTable):
    name = tables.LinkColumn()
    fabric = tables.Column(linkify=True)
    prefix = tables.Column(linkify=True)
    vlan = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    connection_count = tables.Column(verbose_name="Connections")
    tags = TagColumn(url_name="plugins:netbox_peering_manager:peeringnetwork_list")

    class Meta(NetBoxTable.Meta):
        model = PeeringNetwork
        fields = (
            "pk",
            "name",
            "fabric",
            "prefix",
            "vlan",
            "status",
            "connection_count",
            "description",
            "tags",
            "actions",
        )
        default_columns = ("pk", "name", "fabric", "prefix", "status", "connection_count")


class PeeringConnectionTable(NetBoxTable):
    peering_network = tables.Column(linkify=True)
    interface = tables.Column(linkify=True)
    device = tables.Column(accessor="interface__device", linkify=True)
    status = ChoiceFieldColumn()
    tags = TagColumn(url_name="plugins:netbox_peering_manager:peeringconnection_list")

    class Meta(NetBoxTable.Meta):
        model = PeeringConnection
        fields = (
            "pk",
            "peering_network",
            "device",
            "interface",
            "status",
            "description",
            "tags",
            "actions",
        )
        default_columns = ("pk", "peering_network", "device", "interface", "status")


# =============================================================================
# PeeringDB Peer Table
# =============================================================================


class PeeringDBPeerTable(NetBoxTable):
    asn = tables.Column()
    name = tables.Column()
    ipv4_addr = tables.Column(verbose_name="IPv4")
    ipv6_addr = tables.Column(verbose_name="IPv6")
    speed = tables.Column(verbose_name="Speed (Mbps)")
    is_rs_peer = BooleanColumn(verbose_name="RS Peer")

    class Meta(NetBoxTable.Meta):
        model = PeeringDBPeer
        fields = ("asn", "name", "ipv4_addr", "ipv6_addr", "speed", "is_rs_peer")
        default_columns = ("asn", "name", "ipv4_addr", "ipv6_addr", "speed", "is_rs_peer")
