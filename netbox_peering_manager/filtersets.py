import django_filters
import netaddr
from dcim.models import Device, Site
from django.db.models import Q
from ipam.models import ASN, IPAddress
from netaddr.core import AddrFormatError
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from virtualization.models import VirtualMachine

from .choices import PeeringStatusChoices
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
# BFD FilterSet
# =============================================================================


class BFDFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = BFD
        fields = (
            "id",
            "name",
            "description",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


# =============================================================================
# AS Path List FilterSets
# =============================================================================


class ASPathListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ASPathList
        fields = ["id", "name", "description"]

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class ASPathListRuleFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ASPathListRule
        fields = ["id", "action", "aspath_list", "aspath_list_id"]

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(action__icontains=value) | Q(aspath_list__icontains=value) | Q(aspath_list_id__icontains=value)
        return queryset.filter(qs_filter)


class CommunityFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    class Meta:
        model = Community
        fields = (
            "id",
            "value",
            "description",
            "status",
            "tenant",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(value__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class CommunityListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = CommunityList
        fields = (
            "id",
            "name",
            "description",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class CommunityListRuleFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = CommunityListRule
        fields = (
            "id",
            "action",
            "community_list",
            "community_list_id",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(action__icontains=value) | Q(community_list__icontains=value) | Q(community_list_id__icontains=value)
        )
        return queryset.filter(qs_filter)


class BGPSessionFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    remote_as = django_filters.ModelMultipleChoiceFilter(
        field_name="remote_as__asn",
        queryset=ASN.objects.all(),
        to_field_name="asn",
        label="Remote AS (Number)",
    )
    remote_as_id = django_filters.ModelMultipleChoiceFilter(
        field_name="remote_as__id",
        queryset=ASN.objects.all(),
        to_field_name="id",
        label="Remote AS (ID)",
    )
    local_as = django_filters.ModelMultipleChoiceFilter(
        field_name="local_as__asn",
        queryset=ASN.objects.all(),
        to_field_name="asn",
        label="Local AS (Number)",
    )
    local_as_id = django_filters.ModelMultipleChoiceFilter(
        field_name="local_as__id",
        queryset=ASN.objects.all(),
        to_field_name="id",
        label="Local AS (ID)",
    )
    peer_group = django_filters.ModelMultipleChoiceFilter(
        queryset=BGPPeerGroup.objects.all(),
    )
    relationship = django_filters.ModelMultipleChoiceFilter(
        queryset=Relationship.objects.all(),
        label="Relationship",
    )
    bfd = django_filters.ModelMultipleChoiceFilter(
        queryset=BFD.objects.all(),
        label="BFD Profile",
    )
    enabled = django_filters.BooleanFilter(
        label="Enabled",
    )
    import_policies = django_filters.ModelMultipleChoiceFilter(
        queryset=RoutingPolicy.objects.all(),
    )
    export_policies = django_filters.ModelMultipleChoiceFilter(
        queryset=RoutingPolicy.objects.all(),
    )
    local_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name="local_address__id",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label="Local Address (ID)",
    )
    local_address = django_filters.ModelMultipleChoiceFilter(
        field_name="local_address__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label="Local Address",
    )
    remote_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name="remote_address__id",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label="Remote Address (ID)",
    )
    remote_address = django_filters.ModelMultipleChoiceFilter(
        field_name="remote_address__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label="Remote Address",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    virtualmachine_id = django_filters.ModelMultipleChoiceFilter(
        field_name="virtualmachine__id",
        queryset=VirtualMachine.objects.all(),
        to_field_name="id",
        label="VirtualMachine (ID)",
    )
    virtualmachine = django_filters.ModelMultipleChoiceFilter(
        field_name="virtualmachine__name",
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        label="VirtualMachine (name)",
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site__id",
        queryset=Site.objects.all(),
        to_field_name="id",
        label="Site (ID)",
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name="site__name",
        queryset=Site.objects.all(),
        to_field_name="name",
        label="DSite (name)",
    )
    by_remote_address = django_filters.CharFilter(
        method="search_by_remote_ip",
        label="Remote Address",
    )
    by_local_address = django_filters.CharFilter(
        method="search_by_local_ip",
        label="Local Address",
    )

    class Meta:
        model = BGPSession
        fields = (
            "id",
            "name",
            "description",
            "status",
            "enabled",
            "tenant",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(remote_as__asn__icontains=value)
            | Q(name__icontains=value)
            | Q(local_as__asn__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)

    def search_by_remote_ip(self, queryset, _name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(remote_address__address=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_by_local_ip(self, queryset, _name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(local_address__address=query)
        except (AddrFormatError, ValueError):
            return queryset.none()


class RoutingPolicyFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = RoutingPolicy
        fields = (
            "id",
            "name",
            "description",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class RoutingPolicyRuleFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = RoutingPolicyRule
        fields = (
            "id",
            "index",
            "action",
            "description",
            "routing_policy_id",
            "continue_entry",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(index__icontains=value)
            | Q(action__icontains=value)
            | Q(description__icontains=value)
            | Q(routing_policy_id__icontains=value)
            | Q(continue_entry__icontains=value)
        )
        return queryset.filter(qs_filter)


class BGPPeerGroupFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = BGPPeerGroup
        fields = (
            "id",
            "name",
            "description",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


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


class PrefixListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PrefixList
        fields = (
            "id",
            "name",
            "description",
            "family",
            "source_as_set",
            "irr_source",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class PrefixListRuleFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PrefixListRule
        # fields = ['index', 'action', 'prefix_custom', 'ge', 'le', 'prefix_list', 'prefix_list_id']
        fields = (
            "id",
            "index",
            "action",
            "ge",
            "le",
            "prefix_list",
            "prefix_list_id",
        )

    def search(self, queryset, _name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(index__icontains=value)
            | Q(action__icontains=value)
            # | Q(prefix_custom__icontains=value)
            | Q(ge__icontains=value)
            | Q(le__icontains=value)
            | Q(prefix_list__icontains=value)
            | Q(prefix_list_id__icontains=value)
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
