import django_tables2 as tables
from django.utils.safestring import mark_safe
from netbox.tables import NetBoxTable
from netbox.tables.columns import BooleanColumn, ChoiceFieldColumn, ColorColumn, TagColumn

from .models import (
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

AVAILABLE_LABEL = mark_safe('<span class="label label-success">Available</span>')
COL_TENANT = """
 {% if record.tenant %}
     <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
 {% else %}
     &mdash;
 {% endif %}
 """

POLICIES = """
{% for rp in value.all %}
    <a href="{{ rp.get_absolute_url }}">{{ rp }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
    &mdash;
{% endfor %}
"""


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
# BFD Table
# =============================================================================


class BFDTable(NetBoxTable):
    name = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:netbox_peering_manager:bfd_list")

    class Meta(NetBoxTable.Meta):
        model = BFD
        fields = (
            "pk",
            "name",
            "description",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
            "hold_time",
            "tags",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
        )


# =============================================================================
# AS Path List Tables
# =============================================================================


class ASPathListTable(NetBoxTable):
    name = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = ASPathList
        fields = ("pk", "name", "description", "actions")


class ASPathListRuleTable(NetBoxTable):
    aspath_list = tables.Column(linkify=True)
    index = tables.Column(linkify=True)
    action = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ASPathListRule
        fields = (
            "pk",
            "aspath_list",
            "index",
            "action",
            "pattern",
        )


class CommunityTable(NetBoxTable):
    value = tables.LinkColumn()
    status = ChoiceFieldColumn(default=AVAILABLE_LABEL)
    tenant = tables.TemplateColumn(template_code=COL_TENANT)
    tags = TagColumn(url_name="plugins:netbox_peering_manager:community_list")

    class Meta(NetBoxTable.Meta):
        model = Community
        fields = ("pk", "value", "description", "status", "tenant", "tags", "actions")
        default_columns = ("pk", "value", "description", "status", "tenant")


class CommunityListTable(NetBoxTable):
    name = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = CommunityList
        fields = ("pk", "name", "description", "actions")


class CommunityListRuleTable(NetBoxTable):
    community_list = tables.Column(linkify=True)
    action = ChoiceFieldColumn()
    community = tables.Column(
        verbose_name="Community",
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = CommunityListRule
        fields = (
            "pk",
            "community_list",
            "action",
            "community",
        )


class BGPSessionTable(NetBoxTable):
    name = tables.LinkColumn()
    device = tables.LinkColumn()
    virtualmachine = tables.LinkColumn()
    local_address = tables.LinkColumn()
    local_as = tables.LinkColumn()
    remote_address = tables.LinkColumn()
    remote_as = tables.LinkColumn()
    site = tables.LinkColumn()
    peer_group = tables.LinkColumn()
    relationship = tables.LinkColumn()
    bfd = tables.LinkColumn()
    status = ChoiceFieldColumn(default=AVAILABLE_LABEL)
    enabled = BooleanColumn()
    tenant = tables.TemplateColumn(template_code=COL_TENANT)

    class Meta(NetBoxTable.Meta):
        model = BGPSession
        fields = (
            "pk",
            "name",
            "device",
            "virtualmachine",
            "local_address",
            "local_as",
            "remote_address",
            "remote_as",
            "description",
            "peer_group",
            "relationship",
            "bfd",
            "site",
            "status",
            "enabled",
            "tenant",
            "multihop_ttl",
            "service_reference",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "device",
            "virtualmachine",
            "local_address",
            "local_as",
            "remote_address",
            "remote_as",
            "description",
            "relationship",
            "site",
            "status",
            "enabled",
            "tenant",
        )


class RoutingPolicyTable(NetBoxTable):
    name = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = RoutingPolicy
        fields = ("pk", "name", "description", "actions")


class BGPPeerGroupTable(NetBoxTable):
    name = tables.LinkColumn()
    import_policies = tables.TemplateColumn(template_code=POLICIES, orderable=False)
    export_policies = tables.TemplateColumn(template_code=POLICIES, orderable=False)
    tags = TagColumn(url_name="plugins:netbox_peering_manager:bgppeergroup_list")

    class Meta(NetBoxTable.Meta):
        model = BGPPeerGroup
        fields = ("pk", "name", "description", "tags", "import_policies", "export_policies", "actions")
        default_columns = ("pk", "name", "description")


class RoutingPolicyRuleTable(NetBoxTable):
    routing_policy = tables.Column(linkify=True)
    index = tables.Column(linkify=True)
    action = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = RoutingPolicyRule
        fields = (
            "pk",
            "routing_policy",
            "index",
            "match_statements",
            "set_statements",
            "action",
            "description",
            "continue_entry",
        )


class PrefixListTable(NetBoxTable):
    name = tables.LinkColumn()
    family = ChoiceFieldColumn()
    source_as_set = tables.Column(verbose_name="AS-SET")
    irr_source = tables.Column(linkify=True, verbose_name="IRR Source")

    class Meta(NetBoxTable.Meta):
        model = PrefixList
        fields = ("pk", "name", "description", "family", "source_as_set", "irr_source", "actions")
        default_columns = ("pk", "name", "description", "family", "source_as_set")


class PrefixListRuleTable(NetBoxTable):
    prefix_list = tables.Column(linkify=True)
    index = tables.Column(linkify=True)
    action = ChoiceFieldColumn()
    network = tables.Column(
        verbose_name="Prefix",
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = PrefixListRule
        fields = ("pk", "prefix_list", "index", "action", "network", "ge", "le")


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
            "tags",
            "actions",
        )
        default_columns = ("pk", "name", "type", "status", "site", "network_count")


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
