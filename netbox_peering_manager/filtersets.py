import django_filters
from dcim.models import Device, Site
from django.db.models import Q
from ipam.models import ASN
from netbox.filtersets import NetBoxModelFilterSet
from netbox_routing.models import BGPPeer, PrefixList
from tenancy.filtersets import TenancyFilterSet

from .choices import PeeringStatusChoices
from .models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PeeringSession,
    Relationship,
)

# =============================================================================
# Relationship FilterSet
# =============================================================================


class RelationshipFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Relationship
        fields = ("id", "name", "slug", "description")

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(slug__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


# =============================================================================
# PeerASN FilterSet
# =============================================================================


class PeerASNFilterSet(NetBoxModelFilterSet):
    asn_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ASN.objects.all(),
        label="ASN",
    )
    affiliated = django_filters.BooleanFilter()
    peeringdb_id = django_filters.NumberFilter()

    class Meta:
        model = PeerASN
        fields = ["id", "affiliated", "irr_as_set", "peeringdb_id"]

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(asn__asn__icontains=value) | Q(asn__description__icontains=value) | Q(irr_as_set__icontains=value)
        )


# =============================================================================
# IRRSource FilterSet
# =============================================================================


class IRRSourceFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = IRRSource
        fields = (
            "id",
            "name",
            "slug",
            "url",
            "enabled",
        )

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(slug__icontains=value)
            | Q(description__icontains=value)
            | Q(url__icontains=value)
        )
        return queryset.filter(qs_filter)


# =============================================================================
# IRRPrefixListConfig FilterSet
# =============================================================================


class IRRPrefixListConfigFilterSet(NetBoxModelFilterSet):
    prefix_list_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PrefixList.objects.all(),
        label="Prefix List (ID)",
    )
    irr_source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IRRSource.objects.all(),
        label="IRR Source (ID)",
    )
    source_as_set = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = IRRPrefixListConfig
        fields = ("id", "prefix_list_id", "irr_source_id", "source_as_set", "sync_interval")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(prefix_list__name__icontains=value)
            | Q(source_as_set__icontains=value)
            | Q(irr_source__name__icontains=value)
        )
        return queryset.filter(qs_filter)


# =============================================================================
# PeeringSession FilterSet
# =============================================================================


class PeeringSessionFilterSet(NetBoxModelFilterSet):
    bgp_peer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=BGPPeer.objects.all(),
        label="BGP Peer (ID)",
    )
    relationship_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Relationship.objects.all(),
        label="Relationship (ID)",
    )
    peering_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PeeringNetwork.objects.all(),
        label="Peering Network (ID)",
    )

    class Meta:
        model = PeeringSession
        fields = ("id", "bgp_peer_id", "relationship_id", "peering_network_id", "service_reference")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(bgp_peer__name__icontains=value)
            | Q(relationship__name__icontains=value)
            | Q(peering_network__name__icontains=value)
            | Q(service_reference__icontains=value)
        )
        return queryset.filter(qs_filter)


# =============================================================================
# Peering Fabric FilterSets
# =============================================================================


class PeeringFabricTypeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PeeringFabricType
        fields = ("id", "name", "slug", "description")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(slug__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class PeeringFabricFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PeeringFabricType.objects.all(),
        label="Type (ID)",
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label="Site (ID)",
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PeeringStatusChoices,
    )

    class Meta:
        model = PeeringFabric
        fields = ("id", "name", "slug", "status")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(slug__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class PeeringNetworkFilterSet(NetBoxModelFilterSet):
    fabric_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PeeringFabric.objects.all(),
        label="Fabric (ID)",
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PeeringStatusChoices,
    )

    class Meta:
        model = PeeringNetwork
        fields = ("id", "name", "fabric", "status")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(fabric__name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class PeeringConnectionFilterSet(NetBoxModelFilterSet):
    peering_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PeeringNetwork.objects.all(),
        label="Peering Network (ID)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name="interface__device",
        label="Device (ID)",
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PeeringStatusChoices,
    )

    class Meta:
        model = PeeringConnection
        fields = ("id", "peering_network", "interface", "status")

    def search(self, queryset, _name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(peering_network__name__icontains=value)
            | Q(interface__name__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
