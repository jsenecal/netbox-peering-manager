from dcim.models import Device, Interface, Site
from django import forms
from django.utils.translation import gettext as _
from ipam.models import ASN, VLAN, Prefix
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from netbox_routing.models import BGPPeer, BGPPeerTemplate, PrefixList
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    ColorField,
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    SlugField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

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
# Relationship Forms
# =============================================================================


class RelationshipForm(NetBoxModelForm):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = Relationship
        fields = ["name", "slug", "description", "color", "tags", "comments"]


class RelationshipFilterForm(NetBoxModelFilterSetForm):
    model = Relationship
    q = forms.CharField(required=False, label="Search")
    tag = TagFilterField(model)


class RelationshipBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)
    color = ColorField(required=False)

    model = Relationship
    nullable_fields = ["description"]


class RelationshipImportForm(NetBoxModelImportForm):
    class Meta:
        model = Relationship
        fields = ["name", "slug", "description", "color", "tags"]


# =============================================================================
# Peer ASN Forms
# =============================================================================


class PeerASNForm(NetBoxModelForm):
    asn = DynamicModelChoiceField(
        queryset=ASN.objects.all(),
        help_text="Select the NetBox ASN to extend",
    )
    comments = CommentField()

    class Meta:
        model = PeerASN
        fields = [
            "asn",
            "affiliated",
            "irr_as_set",
            "ipv4_max_prefixes",
            "ipv6_max_prefixes",
            "peeringdb_id",
            "tags",
            "comments",
        ]


class PeerASNFilterForm(NetBoxModelFilterSetForm):
    model = PeerASN
    q = forms.CharField(required=False, label="Search")
    affiliated = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=[
                ("", "---------"),
                ("true", "Yes"),
                ("false", "No"),
            ]
        ),
    )
    tag = TagFilterField(model)


class PeerASNBulkEditForm(NetBoxModelBulkEditForm):
    affiliated = forms.NullBooleanField(required=False)
    irr_as_set = forms.CharField(max_length=100, required=False)
    ipv4_max_prefixes = forms.IntegerField(required=False, min_value=0)
    ipv6_max_prefixes = forms.IntegerField(required=False, min_value=0)

    model = PeerASN
    nullable_fields = ["irr_as_set", "ipv4_max_prefixes", "ipv6_max_prefixes", "peeringdb_id"]


class PeerASNImportForm(NetBoxModelImportForm):
    asn = CSVModelChoiceField(
        queryset=ASN.objects.all(),
        to_field_name="asn",
        help_text="ASN number",
    )

    class Meta:
        model = PeerASN
        fields = [
            "asn",
            "affiliated",
            "irr_as_set",
            "ipv4_max_prefixes",
            "ipv6_max_prefixes",
            "peeringdb_id",
            "tags",
        ]


# =============================================================================
# IRRSource Forms
# =============================================================================


class IRRSourceForm(NetBoxModelForm):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = IRRSource
        fields = [
            "name",
            "slug",
            "url",
            "sources",
            "cache_ttl",
            "sync_interval",
            "enabled",
            "description",
            "tags",
            "comments",
        ]


class IRRSourceFilterForm(NetBoxModelFilterSetForm):
    model = IRRSource
    q = forms.CharField(required=False, label="Search")
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "---------"), (True, "Yes"), (False, "No")]),
    )
    tag = TagFilterField(model)


class IRRSourceBulkEditForm(NetBoxModelBulkEditForm):
    url = forms.URLField(required=False)
    sources = forms.CharField(max_length=200, required=False)
    cache_ttl = forms.IntegerField(required=False, min_value=0)
    sync_interval = forms.IntegerField(required=False, min_value=1)
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "---------"), (True, "Yes"), (False, "No")]),
    )
    description = forms.CharField(max_length=200, required=False)

    model = IRRSource
    nullable_fields = ["sources", "cache_ttl", "description"]


class IRRSourceImportForm(NetBoxModelImportForm):
    class Meta:
        model = IRRSource
        fields = ["name", "slug", "url", "sources", "cache_ttl", "sync_interval", "enabled", "description", "tags"]


# =============================================================================
# IRRPrefixListConfig Forms
# =============================================================================


class IRRPrefixListConfigForm(NetBoxModelForm):
    prefix_list = DynamicModelChoiceField(
        queryset=PrefixList.objects.all(),
        label=_("Prefix List"),
    )
    irr_source = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label=_("IRR Source"),
    )

    fieldsets = (
        FieldSet("prefix_list", "tags", name="Prefix List"),
        FieldSet("source_as_set", "irr_source", "sync_interval", name="IRR Sync"),
    )

    class Meta:
        model = IRRPrefixListConfig
        fields = ["prefix_list", "irr_source", "source_as_set", "sync_interval", "tags"]


class IRRPrefixListConfigFilterForm(NetBoxModelFilterSetForm):
    model = IRRPrefixListConfig
    q = forms.CharField(required=False, label="Search")
    irr_source_id = DynamicModelMultipleChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label="IRR Source",
    )
    tag = TagFilterField(model)


class IRRPrefixListConfigBulkEditForm(NetBoxModelBulkEditForm):
    irr_source = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
    )
    source_as_set = forms.CharField(max_length=100, required=False)
    sync_interval = forms.IntegerField(required=False, min_value=1)

    model = IRRPrefixListConfig
    nullable_fields = ["irr_source", "source_as_set"]


class IRRPrefixListConfigImportForm(NetBoxModelImportForm):
    prefix_list = CSVModelChoiceField(
        queryset=PrefixList.objects.all(),
        to_field_name="name",
        help_text="Prefix list name",
    )
    irr_source = CSVModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        to_field_name="name",
    )

    class Meta:
        model = IRRPrefixListConfig
        fields = ["prefix_list", "irr_source", "source_as_set", "sync_interval", "tags"]


# =============================================================================
# PeeringSession Forms
# =============================================================================


class PeeringSessionForm(NetBoxModelForm):
    bgp_peer = DynamicModelChoiceField(
        queryset=BGPPeer.objects.all(),
        label=_("BGP Peer"),
    )
    relationship = DynamicModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
    )
    peering_network = DynamicModelChoiceField(
        queryset=PeeringNetwork.objects.all(),
        required=False,
    )

    fieldsets = (
        FieldSet("bgp_peer", "relationship", "peering_network", "tags", name="Peering Session"),
        FieldSet("service_reference", name="Reference"),
    )

    class Meta:
        model = PeeringSession
        fields = ["bgp_peer", "relationship", "peering_network", "service_reference", "tags"]


class PeeringSessionFilterForm(NetBoxModelFilterSetForm):
    model = PeeringSession
    q = forms.CharField(required=False, label="Search")
    relationship_id = DynamicModelMultipleChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        label="Relationship",
    )
    peering_network_id = DynamicModelMultipleChoiceField(
        queryset=PeeringNetwork.objects.all(),
        required=False,
        label="Peering Network",
    )
    tag = TagFilterField(model)


class PeeringSessionBulkEditForm(NetBoxModelBulkEditForm):
    relationship = DynamicModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
    )
    peering_network = DynamicModelChoiceField(
        queryset=PeeringNetwork.objects.all(),
        required=False,
    )
    service_reference = forms.CharField(max_length=100, required=False)

    model = PeeringSession
    nullable_fields = ["relationship", "peering_network", "service_reference"]


class PeeringSessionImportForm(NetBoxModelImportForm):
    bgp_peer = CSVModelChoiceField(
        queryset=BGPPeer.objects.all(),
        to_field_name="name",
        help_text="BGP peer name",
    )
    relationship = CSVModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        to_field_name="name",
    )
    peering_network = CSVModelChoiceField(
        queryset=PeeringNetwork.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Peering network name",
    )

    class Meta:
        model = PeeringSession
        fields = ["bgp_peer", "relationship", "peering_network", "service_reference", "tags"]


# =============================================================================
# PeeringFabricType Forms
# =============================================================================


class PeeringFabricTypeForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        model = PeeringFabricType
        fields = ["name", "slug", "description", "color", "tags"]


class PeeringFabricTypeFilterForm(NetBoxModelFilterSetForm):
    model = PeeringFabricType
    q = forms.CharField(required=False, label="Search")
    tag = TagFilterField(model)


class PeeringFabricTypeBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)
    color = ColorField(required=False)

    model = PeeringFabricType
    nullable_fields = ["description"]


class PeeringFabricTypeImportForm(NetBoxModelImportForm):
    class Meta:
        model = PeeringFabricType
        fields = ["name", "slug", "description", "color"]


# =============================================================================
# PeeringFabric Forms
# =============================================================================


class PeeringFabricForm(NetBoxModelForm):
    slug = SlugField()
    type = DynamicModelChoiceField(
        queryset=PeeringFabricType.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    peer_group = DynamicModelChoiceField(
        queryset=BGPPeerTemplate.objects.all(),
        required=False,
        label=_("Peer Template"),
    )
    peeringdb_ix_id = forms.IntegerField(
        required=False,
        label="PeeringDB IX ID",
        help_text="Enter PeeringDB IX ID to link and enable sync",
    )
    comments = CommentField()

    class Meta:
        model = PeeringFabric
        fields = [
            "name",
            "slug",
            "description",
            "type",
            "status",
            "site",
            "tenant",
            "peer_group",
            "peeringdb_ix_id",
            "tags",
            "comments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate peeringdb_ix_id if fabric has PeeringDB link
        if self.instance and self.instance.pk and hasattr(self.instance, "peeringdb") and self.instance.peeringdb:
            self.fields["peeringdb_ix_id"].initial = self.instance.peeringdb.ix_id

    def save(self, commit=True):
        instance = super().save(commit)
        ix_id = self.cleaned_data.get("peeringdb_ix_id")

        if ix_id:
            from netbox_peering_manager.services import link_fabric_to_peeringdb

            link_fabric_to_peeringdb(instance, ix_id, sync=False)
        elif hasattr(instance, "peeringdb") and instance.peeringdb:
            # Remove link if IX ID cleared
            instance.peeringdb.delete()

        return instance


class PeeringFabricFilterForm(NetBoxModelFilterSetForm):
    model = PeeringFabric
    q = forms.CharField(required=False, label="Search")
    type_id = DynamicModelMultipleChoiceField(
        queryset=PeeringFabricType.objects.all(),
        required=False,
        label="Type",
    )
    status = forms.MultipleChoiceField(
        choices=PeeringStatusChoices,
        required=False,
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label="Tenant",
    )
    tag = TagFilterField(model)


class PeeringFabricBulkEditForm(NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        queryset=PeeringFabricType.objects.all(),
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PeeringStatusChoices),
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )
    description = forms.CharField(max_length=200, required=False)

    model = PeeringFabric
    nullable_fields = ["type", "site", "tenant", "description"]


class PeeringFabricImportForm(NetBoxModelImportForm):
    type = CSVModelChoiceField(
        queryset=PeeringFabricType.objects.all(),
        required=False,
        to_field_name="name",
    )
    status = CSVChoiceField(choices=PeeringStatusChoices, required=False)
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name="name",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
    )

    class Meta:
        model = PeeringFabric
        fields = ["name", "slug", "description", "type", "status", "site", "tenant"]


# =============================================================================
# PeeringNetwork Forms
# =============================================================================


class PeeringNetworkForm(NetBoxModelForm):
    fabric = DynamicModelChoiceField(
        queryset=PeeringFabric.objects.all(),
    )
    prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = PeeringNetwork
        fields = ["fabric", "name", "prefix", "vlan", "status", "description", "tags", "comments"]


class PeeringNetworkFilterForm(NetBoxModelFilterSetForm):
    model = PeeringNetwork
    q = forms.CharField(required=False, label="Search")
    fabric_id = DynamicModelMultipleChoiceField(
        queryset=PeeringFabric.objects.all(),
        required=False,
        label="Fabric",
    )
    status = forms.MultipleChoiceField(
        choices=PeeringStatusChoices,
        required=False,
    )
    tag = TagFilterField(model)


class PeeringNetworkBulkEditForm(NetBoxModelBulkEditForm):
    fabric = DynamicModelChoiceField(
        queryset=PeeringFabric.objects.all(),
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PeeringStatusChoices),
        required=False,
    )
    description = forms.CharField(max_length=200, required=False)

    model = PeeringNetwork
    nullable_fields = ["vlan", "description"]


class PeeringNetworkImportForm(NetBoxModelImportForm):
    fabric = CSVModelChoiceField(
        queryset=PeeringFabric.objects.all(),
        to_field_name="name",
    )
    prefix = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name="vid",
    )
    status = CSVChoiceField(choices=PeeringStatusChoices, required=False)

    class Meta:
        model = PeeringNetwork
        fields = ["fabric", "name", "prefix", "vlan", "status", "description"]


# =============================================================================
# PeeringConnection Forms
# =============================================================================


class PeeringConnectionForm(NetBoxModelForm):
    peering_network = DynamicModelChoiceField(
        queryset=PeeringNetwork.objects.all(),
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={"device_id": "$device"},
    )

    class Meta:
        model = PeeringConnection
        fields = ["peering_network", "device", "interface", "status", "description", "tags"]

    fieldsets = (
        FieldSet("peering_network", "device", "interface", "status", "description", name="Connection"),
        FieldSet("tags", name="Tags"),
    )


class PeeringConnectionFilterForm(NetBoxModelFilterSetForm):
    model = PeeringConnection
    q = forms.CharField(required=False, label="Search")
    peering_network_id = DynamicModelMultipleChoiceField(
        queryset=PeeringNetwork.objects.all(),
        required=False,
        label="Peering Network",
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
    )
    status = forms.MultipleChoiceField(
        choices=PeeringStatusChoices,
        required=False,
    )
    tag = TagFilterField(model)


class PeeringConnectionBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(PeeringStatusChoices),
        required=False,
    )
    description = forms.CharField(max_length=200, required=False)

    model = PeeringConnection
    nullable_fields = ["description"]


class PeeringConnectionImportForm(NetBoxModelImportForm):
    peering_network = CSVModelChoiceField(
        queryset=PeeringNetwork.objects.all(),
        to_field_name="name",
    )

    class Meta:
        model = PeeringConnection
        fields = ["peering_network", "interface", "status", "description"]
