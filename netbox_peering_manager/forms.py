from dcim.models import Device, Interface, Site
from django import forms
from django.utils.translation import gettext as _
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
from ipam.formfields import IPNetworkFormField
from ipam.models import ASN, VLAN, IPAddress, Prefix
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    ColorField,
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    SlugField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import APISelect, APISelectMultiple
from virtualization.models import VirtualMachine

from .choices import (
    CommunityStatusChoices,
    PeeringStatusChoices,
    SessionStatusChoices,
)
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
# BFD Forms
# =============================================================================


class BFDForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = BFD
        fields = [
            "name",
            "description",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
            "hold_time",
            "tags",
            "comments",
        ]


class BFDFilterForm(NetBoxModelFilterSetForm):
    model = BFD
    q = forms.CharField(required=False, label="Search")
    tag = TagFilterField(model)


class BFDBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)
    minimum_transmit_interval = forms.IntegerField(required=False, min_value=50, max_value=60000)
    minimum_receive_interval = forms.IntegerField(required=False, min_value=50, max_value=60000)
    detect_multiplier = forms.IntegerField(required=False, min_value=1, max_value=255)
    hold_time = forms.IntegerField(required=False, min_value=50, max_value=60000)

    model = BFD
    nullable_fields = ["description", "hold_time"]


class BFDImportForm(NetBoxModelImportForm):
    class Meta:
        model = BFD
        fields = [
            "name",
            "description",
            "minimum_transmit_interval",
            "minimum_receive_interval",
            "detect_multiplier",
            "hold_time",
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
# AS Path List Forms
# =============================================================================


class ASPathListFilterForm(NetBoxModelFilterSetForm):
    model = ASPathList
    q = forms.CharField(required=False, label="Search")

    tag = TagFilterField(model)


class ASPathListRuleFilterForm(NetBoxModelFilterSetForm):
    model = ASPathListRule
    q = forms.CharField(required=False, label="Search")
    aspath_list = DynamicModelChoiceField(queryset=ASPathList.objects.all(), required=False)
    tag = TagFilterField(model)


class ASPathListForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = ASPathList
        fields = ["name", "description", "tags", "comments"]


class ASPathListBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)

    model = ASPathList
    nullable_fields = [
        "description",
    ]


class ASPathListImportForm(NetBoxModelImportForm):
    class Meta:
        model = ASPathList
        fields = ["name", "description", "tags"]


class ASPathListRuleImportForm(NetBoxModelImportForm):
    class Meta:
        model = ASPathListRule
        fields = ["aspath_list", "index", "action", "pattern", "description", "tags", "comments"]


class ASPathListRuleForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = ASPathListRule
        fields = ["aspath_list", "index", "action", "pattern", "description", "tags", "comments"]


class CommunityForm(NetBoxModelForm):
    status = forms.ChoiceField(
        required=False,
        choices=CommunityStatusChoices,
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    comments = CommentField()

    class Meta:
        model = Community
        fields = ["value", "description", "status", "tenant", "tags", "comments"]


class CommunityFilterForm(NetBoxModelFilterSetForm):
    q = forms.CharField(required=False, label="Search")
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    status = forms.MultipleChoiceField(
        choices=CommunityStatusChoices,
        required=False,
    )
    site = DynamicModelChoiceField(queryset=Site.objects.all(), required=False)

    tag = TagFilterField(Community)

    model = Community


class CommunityBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    description = forms.CharField(max_length=200, required=False)
    status = forms.ChoiceField(
        required=False,
        choices=CommunityStatusChoices,
    )

    model = Community
    nullable_fields = [
        "tenant",
        "description",
    ]


class CommunityImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Assigned tenant"),
    )

    status = CSVChoiceField(choices=CommunityStatusChoices, help_text=_("Operational status"))

    class Meta:
        model = Community
        fields = ("value", "description", "tags")


class CommunityListFilterForm(NetBoxModelFilterSetForm):
    model = CommunityList
    q = forms.CharField(required=False, label="Search")

    tag = TagFilterField(model)


class CommunityListForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = CommunityList
        fields = ["name", "description", "tags", "comments"]


class CommunityListBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)

    model = CommunityList
    nullable_fields = [
        "description",
    ]


class CommunityListImportForm(NetBoxModelImportForm):
    class Meta:
        model = CommunityList
        fields = ("name", "description", "tags")


class CommunityListRuleForm(NetBoxModelForm):
    community = DynamicModelChoiceField(
        queryset=Community.objects.all(),
        required=False,
        help_text="Community",
    )

    comments = CommentField()

    class Meta:
        model = CommunityListRule
        fields = ["community_list", "action", "community", "tags", "comments"]


class BGPSessionForm(NetBoxModelForm):
    name = forms.CharField(max_length=64, required=True)
    site = DynamicModelChoiceField(queryset=Site.objects.all(), required=False)
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False, query_params={"site_id": "$site"})
    virtualmachine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, query_params={"site_id": "$site"}
    )

    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    local_as = DynamicModelChoiceField(
        queryset=ASN.objects.all(),
        query_params={"site_id": "$site"},
        label=_("Local AS"),
    )
    remote_as = DynamicModelChoiceField(queryset=ASN.objects.all(), label=_("Remote AS"))
    local_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={"device_id": "$device"},
        selector=True,
        quick_add=True,
        label=_("Local IP Address"),
    )
    remote_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        selector=True,
        quick_add=True,
        label=_("Remote IP Address"),
    )
    peer_group = DynamicModelChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/plugins/bgp/peer-group/",
        ),
    )
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    prefix_list_in = DynamicModelChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/plugins/bgp/prefix-list/",
        ),
    )
    prefix_list_out = DynamicModelChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/plugins/bgp/prefix-list/",
        ),
    )
    # Phase 1: New fields
    relationship = DynamicModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        widget=APISelect(api_url="/api/plugins/bgp/relationship/"),
        help_text=_("Type of BGP relationship"),
    )
    bfd = DynamicModelChoiceField(
        queryset=BFD.objects.all(),
        required=False,
        widget=APISelect(api_url="/api/plugins/bgp/bfd/"),
        label=_("BFD Profile"),
        help_text=_("BFD configuration for this session"),
    )
    multihop_ttl = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        max_value=255,
        label=_("Multihop TTL"),
        help_text=_("TTL for eBGP multihop (1 = directly connected)"),
    )
    service_reference = forms.CharField(
        max_length=100,
        required=False,
        label=_("Service Reference"),
        help_text=_("External reference ID (e.g., ticket number)"),
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Enabled"),
        help_text=_("Administrative enable/disable state"),
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "site",
            "device",
            "virtualmachine",
            "status",
            "enabled",
            "relationship",
            "peer_group",
            "tenant",
            "tags",
            name="Session",
        ),
        FieldSet("remote_as", "remote_address", name="Remote"),
        FieldSet("local_as", "local_address", name="Local"),
        FieldSet("import_policies", "export_policies", name="Policies"),
        FieldSet("prefix_list_in", "prefix_list_out", name="Prefixes"),
        FieldSet("bfd", "multihop_ttl", "service_reference", name="Advanced"),
    )

    class Meta:
        model = BGPSession
        fields = [
            "name",
            "site",
            "device",
            "virtualmachine",
            "local_as",
            "remote_as",
            "local_address",
            "remote_address",
            "description",
            "status",
            "enabled",
            "relationship",
            "peer_group",
            "tenant",
            "tags",
            "import_policies",
            "export_policies",
            "prefix_list_in",
            "prefix_list_out",
            "bfd",
            "multihop_ttl",
            "service_reference",
            "comments",
        ]

        widgets = {
            "status": forms.Select(),
        }


class BGPSessionImportForm(NetBoxModelImportForm):
    site = CSVModelChoiceField(
        label=_("Site"),
        required=False,
        queryset=Site.objects.all(),
        to_field_name="name",
        help_text=_("Assigned site"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Assigned tenant"),
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        help_text=_("Assigned device"),
        required=False,
    )
    virtualmachine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        help_text=_("Assigned virtual machine"),
        required=False,
    )
    status = CSVChoiceField(choices=SessionStatusChoices, required=False, help_text=_("Operational status"))
    local_address = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        help_text=_("Local IP Address"),
    )
    remote_address = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        help_text=_("Remote IP Address"),
    )
    local_as = CSVModelChoiceField(
        queryset=ASN.objects.all(),
        to_field_name="asn",
        help_text=_("Local ASN"),
    )
    remote_as = CSVModelChoiceField(
        queryset=ASN.objects.all(),
        to_field_name="asn",
        help_text=_("Remote ASN"),
    )
    peer_group = CSVModelChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Peer Group"),
    )
    import_policies = CSVModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        to_field_name="name",
        required=False,
        help_text=_("Import policies name"),
    )
    export_policies = CSVModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        to_field_name="name",
        required=False,
        help_text=_("Export policies name"),
    )
    prefix_list_in = CSVModelChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Prefix list In"),
    )
    prefix_list_out = CSVModelChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Prefix List Out"),
    )
    # Phase 1: New fields
    relationship = CSVModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Relationship type"),
    )
    bfd = CSVModelChoiceField(
        queryset=BFD.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("BFD Profile"),
    )

    class Meta:
        model = BGPSession
        fields = [
            "name",
            "device",
            "virtualmachine",
            "site",
            "description",
            "tenant",
            "status",
            "enabled",
            "relationship",
            "peer_group",
            "import_policies",
            "export_policies",
            "local_address",
            "remote_address",
            "local_as",
            "remote_as",
            "tags",
            "prefix_list_in",
            "prefix_list_out",
            "bfd",
            "multihop_ttl",
            "service_reference",
        ]


class BGPSessionFilterForm(NetBoxModelFilterSetForm):
    model = BGPSession
    q = forms.CharField(required=False, label="Search")
    remote_as_id = DynamicModelMultipleChoiceField(queryset=ASN.objects.all(), required=False, label=_("Remote AS"))
    local_as_id = DynamicModelMultipleChoiceField(queryset=ASN.objects.all(), required=False, label=_("Local AS"))
    by_local_address = forms.CharField(required=False, label="Local Address")
    by_remote_address = forms.CharField(required=False, label="Remote Address")
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label=_("Device"))
    virtualmachine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label=_("VirtualMachine")
    )
    site_id = DynamicModelMultipleChoiceField(queryset=Site.objects.all(), required=False, label=_("Site"))
    status = forms.MultipleChoiceField(
        choices=SessionStatusChoices,
        required=False,
    )
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "---------"), (True, "Yes"), (False, "No")]),
    )
    relationship = DynamicModelMultipleChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/relationship/"),
    )
    peer_group = DynamicModelMultipleChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/peer-group/"),
    )
    bfd = DynamicModelMultipleChoiceField(
        queryset=BFD.objects.all(),
        required=False,
        label=_("BFD Profile"),
        widget=APISelectMultiple(api_url="/api/plugins/bgp/bfd/"),
    )
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    prefix_list_in = DynamicModelMultipleChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/prefix-list/"),
    )
    prefix_list_out = DynamicModelMultipleChoiceField(
        queryset=PrefixList.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/prefix-list/"),
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    tag = TagFilterField(model)


class BGPSessionBulkEditForm(NetBoxModelBulkEditForm):
    device = DynamicModelChoiceField(
        label=_("Device"),
        queryset=Device.objects.all(),
        required=False,
    )
    virtualmachine = DynamicModelChoiceField(
        label=_("Virtual Machine"),
        queryset=VirtualMachine.objects.all(),
        required=False,
    )
    site = DynamicModelChoiceField(label=_("Site"), queryset=Site.objects.all(), required=False)

    status = forms.ChoiceField(label=_("Status"), choices=add_blank_choice(SessionStatusChoices), required=False)
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "---------"), (True, "Yes"), (False, "No")]),
    )
    description = forms.CharField(label=_("Description"), max_length=200, required=False)
    tenant = DynamicModelChoiceField(label=_("Tenant"), queryset=Tenant.objects.all(), required=False)
    local_as = DynamicModelChoiceField(queryset=ASN.objects.all(), required=False)
    remote_as = DynamicModelChoiceField(queryset=ASN.objects.all(), required=False)
    relationship = DynamicModelChoiceField(
        queryset=Relationship.objects.all(),
        required=False,
        widget=APISelect(api_url="/api/plugins/bgp/relationship/"),
    )
    peer_group = DynamicModelChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/plugins/bgp/peer-group/",
        ),
    )
    bfd = DynamicModelChoiceField(
        queryset=BFD.objects.all(),
        required=False,
        label=_("BFD Profile"),
        widget=APISelect(api_url="/api/plugins/bgp/bfd/"),
    )
    multihop_ttl = forms.IntegerField(required=False, min_value=1, max_value=255, label=_("Multihop TTL"))
    service_reference = forms.CharField(max_length=100, required=False, label=_("Service Reference"))
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )

    model = BGPSession

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "site",
            "device",
            "virtualmachine",
            "status",
            "enabled",
            "relationship",
            "peer_group",
            "tenant",
            "tags",
            name="Session",
        ),
        FieldSet("remote_as", "remote_address", name="Remote"),
        FieldSet("local_as", "local_address", name="Local"),
        FieldSet("import_policies", "export_policies", name="Policies"),
        FieldSet("prefix_list_in", "prefix_list_out", name="Prefixes"),
        FieldSet("bfd", "multihop_ttl", "service_reference", name="Advanced"),
    )

    nullable_fields = [
        "tenant",
        "description",
        "relationship",
        "peer_group",
        "bfd",
        "service_reference",
        "import_policies",
        "export_policies",
        "prefix_list_in",
        "prefix_list_out",
    ]


class RoutingPolicyFilterForm(NetBoxModelFilterSetForm):
    model = RoutingPolicy
    q = forms.CharField(required=False, label="Search")

    tag = TagFilterField(model)


class RoutingPolicyForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = RoutingPolicy
        fields = ["name", "description", "tags", "comments"]


class RoutingPolicyImportForm(NetBoxModelImportForm):
    class Meta:
        model = RoutingPolicy
        fields = ("name", "description", "tags")


class RoutingPolicyBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)

    model = RoutingPolicy
    nullable_fields = [
        "description",
    ]


class BGPPeerGroupFilterForm(NetBoxModelFilterSetForm):
    model = BGPPeerGroup
    q = forms.CharField(required=False, label="Search")

    tag = TagFilterField(model)


class BGPPeerGroupForm(NetBoxModelForm):
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    comments = CommentField()

    class Meta:
        model = BGPPeerGroup
        fields = [
            "name",
            "description",
            "import_policies",
            "export_policies",
            "tags",
            "comments",
        ]


class BGPPeerGroupImportForm(NetBoxModelImportForm):
    import_policies = CSVModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        to_field_name="name",
        required=False,
        help_text=_("Import policies name"),
    )
    export_policies = CSVModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        to_field_name="name",
        required=False,
        help_text=_("Export policies name"),
    )

    class Meta:
        model = BGPPeerGroup
        fields = ("name", "description", "import_policies", "export_policies", "tags")


class BGPPeerGroupBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)

    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(api_url="/api/plugins/bgp/routing-policy/"),
    )

    model = BGPPeerGroup
    nullable_fields = ["description", "import_policies", "export_policies"]


class RoutingPolicyRuleForm(NetBoxModelForm):
    continue_entry = forms.IntegerField(
        required=False,
        label="Continue",
        help_text="Null for disable, 0 to next entry, or any sequence number",
    )
    match_community = DynamicModelMultipleChoiceField(
        queryset=Community.objects.all(),
        required=False,
    )
    match_community_list = DynamicModelMultipleChoiceField(
        queryset=CommunityList.objects.all(),
        required=False,
    )

    match_ip_address = DynamicModelMultipleChoiceField(
        queryset=PrefixList.objects.all(), required=False, query_params={"family": "ipv4"}
    )

    match_ipv6_address = DynamicModelMultipleChoiceField(
        queryset=PrefixList.objects.all(), required=False, query_params={"family": "ipv6"}
    )

    match_aspath_list = DynamicModelMultipleChoiceField(
        queryset=ASPathList.objects.all(),
        required=False,
    )

    match_custom = forms.JSONField(
        label="Custom Match",
        help_text='Any custom match statements, e.g., {"ip nexthop": "1.1.1.1"}',
        required=False,
    )
    set_actions = forms.JSONField(
        label="Set statements",
        help_text='Set statements, e.g., {"as-path prepend": [12345,12345]}',
        required=False,
    )
    comments = CommentField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = RoutingPolicyRule
        fields = [
            "routing_policy",
            "index",
            "action",
            "continue_entry",
            "match_community",
            "match_community_list",
            "match_ip_address",
            "match_ipv6_address",
            "match_aspath_list",
            "match_custom",
            "set_actions",
            "description",
            "tags",
            "comments",
        ]


class RoutingPolicyRuleImportForm(NetBoxModelImportForm):
    class Meta:
        model = RoutingPolicyRule
        fields = (
            "routing_policy",
            "index",
            "action",
            "continue_entry",
            "match_community",
            "match_community_list",
            "match_ip_address",
            "match_ipv6_address",
            "match_custom",
            "set_actions",
            "description",
            "tags",
            "comments",
        )


class PrefixListFilterForm(NetBoxModelFilterSetForm):
    model = PrefixList
    q = forms.CharField(required=False, label="Search")
    family = forms.MultipleChoiceField(
        choices=CoreIPAddressFamilyChoices,
        required=False,
    )
    irr_source_id = DynamicModelMultipleChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label="IRR Source",
    )
    tag = TagFilterField(model)


class PrefixListForm(NetBoxModelForm):
    irr_source = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label=_("IRR Source"),
        help_text=_("IRR source for AS-SET queries"),
    )
    comments = CommentField()

    fieldsets = (
        FieldSet("name", "description", "family", "tags", name="Prefix List"),
        FieldSet("source_as_set", "irr_source", name="IRR Sync"),
    )

    class Meta:
        model = PrefixList
        fields = ["name", "description", "family", "source_as_set", "irr_source", "tags", "comments"]


class PrefixListImportForm(NetBoxModelImportForm):
    family = CSVChoiceField(choices=CoreIPAddressFamilyChoices, required=True, help_text=_("Family address"))
    irr_source = CSVModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("IRR source for AS-SET queries"),
    )

    class Meta:
        model = PrefixList
        fields = ("name", "description", "family", "source_as_set", "irr_source", "tags")


class PrefixListBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(max_length=200, required=False)
    family = forms.ChoiceField(
        label=_("Family"),
        required=False,
        choices=CoreIPAddressFamilyChoices,
    )
    source_as_set = forms.CharField(
        max_length=100,
        required=False,
        label=_("Source AS-SET"),
        help_text=_("AS-SET to sync from IRR"),
    )
    irr_source = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label=_("IRR Source"),
    )

    model = PrefixList
    nullable_fields = ["description", "source_as_set", "irr_source"]


class PrefixListRuleImportForm(NetBoxModelImportForm):
    class Meta:
        model = PrefixListRule
        fields = (
            "prefix_list",
            "index",
            "action",
            "prefix",
            "prefix_custom",
            "ge",
            "le",
            "tags",
            "comments",
        )


class PrefixListRuleForm(NetBoxModelForm):
    prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text="NetBox Prefix Object",
    )
    prefix_custom = IPNetworkFormField(
        required=False,
        label="Prefix",
        help_text="Just IP field for define special prefix like 0.0.0.0/0",
    )
    ge = forms.IntegerField(
        label="Greater than or equal to",
        required=False,
    )
    le = forms.IntegerField(
        label="Less than or equal to",
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = PrefixListRule
        fields = [
            "prefix_list",
            "index",
            "action",
            "prefix",
            "prefix_custom",
            "ge",
            "le",
            "tags",
            "comments",
        ]


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
        queryset=BGPPeerGroup.objects.all(),
        required=False,
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
