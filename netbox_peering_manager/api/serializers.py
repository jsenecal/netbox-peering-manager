from dcim.api.serializers import DeviceSerializer, InterfaceSerializer, SiteSerializer
from dcim.models import Device
from extras.models import ConfigTemplate
from ipam.api.field_serializers import IPNetworkField
from ipam.api.serializers import ASNSerializer, IPAddressSerializer, PrefixSerializer, VLANSerializer
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField
from tenancy.api.serializers import TenantSerializer
from virtualization.api.serializers import VirtualMachineSerializer

from netbox_peering_manager.choices import CommunityStatusChoices, PeeringStatusChoices, SessionStatusChoices
from netbox_peering_manager.models import (
    BFD,
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricPeeringDB,
    PeeringFabricType,
    PeeringNetwork,
    PrefixList,
    PrefixListRule,
    Relationship,
    RoutingPolicy,
    RoutingPolicyRule,
)


class ASPathListSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:aspathlist-detail")

    class Meta:
        model = ASPathList
        fields = [
            "id",
            "url",
            "name",
            "display",
            "description",
            "tags",
            "custom_fields",
            "comments",
        ]
        brief_fields = ("id", "url", "display", "name", "description")


class ASPathListRuleSerializer(NetBoxModelSerializer):
    aspath_list = ASPathListSerializer(nested=True)

    class Meta:
        model = ASPathListRule
        fields = [
            "id",
            "description",
            "tags",
            "custom_fields",
            "display",
            "aspath_list",
            "created",
            "last_updated",
            "index",
            "action",
            "pattern",
            "comments",
        ]
        brief_fields = ("id", "display", "description")


class RelationshipSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:relationship-detail")

    class Meta:
        model = Relationship
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "color",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "color")


class BFDSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:bfd-detail")

    class Meta:
        model = BFD
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
            "hold_time",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "description")


class IRRSourceSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:irrsource-detail")
    api_endpoint = serializers.URLField(source="url", read_only=False)

    class Meta:
        model = IRRSource
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "api_endpoint",
            "sources",
            "cache_ttl",
            "sync_interval",
            "enabled",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "enabled")


class PeerASNSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peerasn-detail")
    asn = ASNSerializer(nested=True)
    session_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PeerASN
        fields = [
            "id",
            "url",
            "display",
            "asn",
            "affiliated",
            "irr_as_set",
            "ipv4_max_prefixes",
            "ipv6_max_prefixes",
            "peeringdb_id",
            "peeringdb_last_sync",
            "session_count",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "asn", "affiliated"]


class RoutingPolicySerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:routingpolicy-detail")

    class Meta:
        model = RoutingPolicy
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "weight",
            "address_family",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "description")


class PrefixListSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:prefixlist-detail")
    irr_source = IRRSourceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = PrefixList
        fields = (
            "id",
            "url",
            "name",
            "display",
            "description",
            "family",
            "source_as_set",
            "irr_source",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "description", "family")


class BGPPeerGroupSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:bgppeergroup-detail")

    import_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=RoutingPolicySerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    export_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=RoutingPolicySerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )

    class Meta:
        model = BGPPeerGroup
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "import_policies",
            "export_policies",
            "comments",
            "custom_fields",
        )
        brief_fields = ("id", "url", "display", "name", "description")


class BGPSessionSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:bgpsession-detail")
    status = ChoiceField(choices=SessionStatusChoices, required=False)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    device = DeviceSerializer(nested=True, required=False, allow_null=True)
    virtualmachine = VirtualMachineSerializer(nested=True, required=False, allow_null=True)
    local_address = IPAddressSerializer(nested=True, required=True, allow_null=False)
    remote_address = IPAddressSerializer(nested=True, required=True, allow_null=False)
    local_as = ASNSerializer(nested=True, required=True, allow_null=False)
    remote_as = PeerASNSerializer(nested=True, required=True, allow_null=False)
    peer_group = BGPPeerGroupSerializer(nested=True, required=False, allow_null=True)
    relationship = RelationshipSerializer(nested=True, required=False, allow_null=True)
    bfd = BFDSerializer(nested=True, required=False, allow_null=True)
    prefix_list_in = PrefixListSerializer(nested=True, required=False, allow_null=True)
    prefix_list_out = PrefixListSerializer(nested=True, required=False, allow_null=True)
    import_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=RoutingPolicySerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    export_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=RoutingPolicySerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )

    class Meta:
        model = BGPSession
        fields = (
            "id",
            "url",
            "tags",
            "custom_fields",
            "display",
            "status",
            "password",
            "enabled",
            "site",
            "tenant",
            "device",
            "virtualmachine",
            "local_address",
            "remote_address",
            "local_as",
            "remote_as",
            "peer_group",
            "relationship",
            "bfd",
            "multihop_ttl",
            "service_reference",
            "import_policies",
            "export_policies",
            "prefix_list_in",
            "prefix_list_out",
            "created",
            "last_updated",
            "name",
            "description",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "status", "local_as", "remote_as")

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance is not None and instance.peer_group:
            for pol in instance.peer_group.import_policies.difference(instance.import_policies.all()):
                ret["import_policies"].append(
                    RoutingPolicySerializer(
                        pol,
                        context={"request": self.context["request"]},
                        nested=True,
                    ).data
                )
            for pol in instance.peer_group.export_policies.difference(instance.export_policies.all()):
                ret["export_policies"].append(
                    RoutingPolicySerializer(
                        pol,
                        context={"request": self.context["request"]},
                        nested=True,
                    ).data
                )
        return ret


class CommunitySerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=CommunityStatusChoices, required=False)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:community-detail")

    class Meta:
        model = Community
        fields = (
            "id",
            "url",
            "tags",
            "custom_fields",
            "display",
            "status",
            "tenant",
            "created",
            "last_updated",
            "description",
            "value",
            "site",
            "role",
            "comments",
        )
        brief_fields = ("id", "url", "display", "value", "description")


class CommunityListSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:communitylist-detail")

    class Meta:
        model = CommunityList
        fields = (
            "id",
            "url",
            "name",
            "display",
            "description",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "description")


class CommunityListRuleSerializer(NetBoxModelSerializer):
    community_list = CommunityListSerializer(nested=True)
    community = CommunitySerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = CommunityListRule
        fields = (
            "id",
            "tags",
            "custom_fields",
            "display",
            "description",
            "community_list",
            "created",
            "last_updated",
            "action",
            "community",
            "comments",
        )
        brief_fields = ("id", "display", "description")


class RoutingPolicyRuleSerializer(NetBoxModelSerializer):
    match_ip_address = SerializedPKRelatedField(
        queryset=PrefixList.objects.all(),
        serializer=PrefixListSerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    match_ipv6_address = SerializedPKRelatedField(
        queryset=PrefixList.objects.all(),
        serializer=PrefixListSerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    routing_policy = RoutingPolicySerializer(nested=True)

    match_community = SerializedPKRelatedField(
        queryset=Community.objects.all(),
        serializer=CommunitySerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    match_community_list = SerializedPKRelatedField(
        queryset=CommunityList.objects.all(),
        serializer=CommunityListSerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )
    match_aspath_list = SerializedPKRelatedField(
        queryset=ASPathList.objects.all(),
        serializer=ASPathListSerializer,
        nested=True,
        required=False,
        allow_null=True,
        many=True,
    )

    class Meta:
        model = RoutingPolicyRule
        fields = (
            "id",
            "index",
            "display",
            "action",
            "match_ip_address",
            "routing_policy",
            "match_community",
            "match_community_list",
            "match_aspath_list",
            "match_custom",
            "set_actions",
            "match_ipv6_address",
            "description",
            "continue_entry",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "display", "description")


class PrefixListRuleSerializer(NetBoxModelSerializer):
    prefix_list = PrefixListSerializer(nested=True)
    prefix = PrefixSerializer(nested=True, required=False, allow_null=True)
    prefix_custom = IPNetworkField(required=False, allow_null=True)

    class Meta:
        model = PrefixListRule
        fields = (
            "id",
            "description",
            "tags",
            "custom_fields",
            "display",
            "prefix_list",
            "created",
            "last_updated",
            "index",
            "action",
            "prefix_custom",
            "ge",
            "le",
            "prefix",
            "comments",
        )
        brief_fields = ("id", "display", "description")


# =============================================================================
# Peering Fabric Serializers
# =============================================================================


class PeeringFabricTypeSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peeringfabrictype-detail")

    class Meta:
        model = PeeringFabricType
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "color",
            "tags",
            "custom_fields",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "color")


class PeeringFabricPeeringDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeeringFabricPeeringDB
        fields = ["ix_id", "name", "city", "country", "website", "last_sync"]


class PeeringFabricSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peeringfabric-detail")
    status = ChoiceField(choices=PeeringStatusChoices, required=False)
    type = PeeringFabricTypeSerializer(nested=True, required=False, allow_null=True)
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    peer_group = BGPPeerGroupSerializer(nested=True, required=False, allow_null=True)
    peeringdb = PeeringFabricPeeringDBSerializer(read_only=True)

    class Meta:
        model = PeeringFabric
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "type",
            "status",
            "site",
            "tenant",
            "peer_group",
            "peeringdb",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "status")


class PeeringNetworkSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peeringnetwork-detail")
    status = ChoiceField(choices=PeeringStatusChoices, required=False)
    fabric = PeeringFabricSerializer(nested=True)
    prefix = PrefixSerializer(nested=True)
    vlan = VLANSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = PeeringNetwork
        fields = (
            "id",
            "url",
            "display",
            "fabric",
            "name",
            "prefix",
            "vlan",
            "status",
            "description",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "fabric", "status")


class PeeringConnectionSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peeringconnection-detail")
    status = ChoiceField(choices=PeeringStatusChoices, required=False)
    peering_network = PeeringNetworkSerializer(nested=True)
    interface = InterfaceSerializer(nested=True)

    class Meta:
        model = PeeringConnection
        fields = (
            "id",
            "url",
            "display",
            "peering_network",
            "interface",
            "status",
            "description",
            "tags",
            "custom_fields",
        )
        brief_fields = ("id", "url", "display", "peering_network", "interface", "status")


# =============================================================================
# Configuration Templating Serializers
# =============================================================================


class RenderConfigRequestSerializer(serializers.Serializer):
    """Serializer for render-config API request."""

    template = serializers.PrimaryKeyRelatedField(
        queryset=ConfigTemplate.objects.all(),
        help_text="ID of the ConfigTemplate to render",
    )
    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(),
        required=False,
        allow_null=True,
        help_text="ID of the device to render config for",
    )
    sessions = serializers.PrimaryKeyRelatedField(
        queryset=BGPSession.objects.all(),
        many=True,
        required=False,
        help_text="List of BGP session IDs to include",
    )

    def validate(self, data):
        """Ensure at least device or sessions is provided."""
        if not data.get("device") and not data.get("sessions"):
            msg = "Either 'device' or 'sessions' must be provided."
            raise serializers.ValidationError(msg)
        return data
