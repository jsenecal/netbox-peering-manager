from dcim.api.serializers import InterfaceSerializer, SiteSerializer
from dcim.models import Device
from extras.models import ConfigTemplate
from ipam.api.serializers import ASNSerializer, PrefixSerializer, VLANSerializer
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer
from netbox_routing.api.serializers import BGPPeerSerializer, BGPPeerTemplateSerializer, PrefixListSerializer
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField
from tenancy.api.serializers import TenantSerializer

from netbox_peering_manager.choices import PeeringStatusChoices
from netbox_peering_manager.models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricPeeringDB,
    PeeringFabricType,
    PeeringNetwork,
    PeeringSession,
    Relationship,
)


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


class IRRPrefixListConfigSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:irrprefixlistconfig-detail")
    prefix_list = PrefixListSerializer(nested=True)
    irr_source = IRRSourceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = IRRPrefixListConfig
        fields = (
            "id",
            "url",
            "display",
            "prefix_list",
            "irr_source",
            "source_as_set",
            "sync_interval",
            "tags",
            "custom_fields",
        )
        brief_fields = ("id", "url", "display", "prefix_list", "source_as_set")


class PeerASNSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peerasn-detail")
    asn = ASNSerializer(nested=True)

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
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "asn", "affiliated"]


class PeeringSessionSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:peeringsession-detail")
    bgp_peer = BGPPeerSerializer(nested=True)
    relationship = RelationshipSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = PeeringSession
        fields = (
            "id",
            "url",
            "display",
            "bgp_peer",
            "relationship",
            "peering_network",
            "service_reference",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "bgp_peer", "relationship")


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
    peer_group = BGPPeerTemplateSerializer(nested=True, required=False, allow_null=True)
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
        queryset=PeeringSession.objects.all(),
        many=True,
        required=False,
        help_text="List of PeeringSession IDs to include",
    )

    def validate(self, data):
        """Ensure at least device or sessions is provided."""
        if not data.get("device") and not data.get("sessions"):
            msg = "Either 'device' or 'sessions' must be provided."
            raise serializers.ValidationError(msg)
        return data
