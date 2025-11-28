from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from ipam.fields import IPNetworkField
from netbox.models import NetBoxModel
from utilities.fields import ColorField

from .choices import ActionChoices, CommunityStatusChoices, IPAddressFamilyChoices, SessionStatusChoices


class Relationship(NetBoxModel):
    """
    Defines the type of BGP session relationship (e.g., transit, customer, peer, IXP).
    User-defined relationship types allow flexible classification of BGP sessions.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    color = ColorField(default="9e9e9e")
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:relationship", args=[self.pk])


class BFD(NetBoxModel):
    """
    Bidirectional Forwarding Detection (BFD) configuration profile.
    Reusable BFD settings that can be applied to multiple BGP sessions.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    minimum_transmit_interval = models.PositiveIntegerField(
        default=300,
        help_text="Minimum interval (in milliseconds) between transmitted BFD packets",
        validators=[MinValueValidator(50), MaxValueValidator(60000)],
    )
    minimum_receive_interval = models.PositiveIntegerField(
        default=300,
        help_text="Minimum interval (in milliseconds) between received BFD packets",
        validators=[MinValueValidator(50), MaxValueValidator(60000)],
    )
    detect_multiplier = models.PositiveSmallIntegerField(
        default=3,
        help_text="Number of missed packets before session is declared down",
        validators=[MinValueValidator(1), MaxValueValidator(255)],
    )
    hold_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional hold time override (in milliseconds)",
        validators=[MinValueValidator(50), MaxValueValidator(60000)],
    )
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name = "BFD Profile"
        verbose_name_plural = "BFD Profiles"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:bfd", args=[self.pk])

    @property
    def calculated_hold_time(self):
        """Calculate hold time as minimum_receive_interval * detect_multiplier if not explicitly set."""
        if self.hold_time:
            return self.hold_time
        return self.minimum_receive_interval * self.detect_multiplier


class ASPathList(NetBoxModel):
    """
    as-path access list, as-path filter
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "AS Path Lists"
        unique_together = ["name", "description"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:aspathlist", args=[self.pk])


class ASPathListRule(NetBoxModel):
    """
    Rules for AS Path List
    """

    aspath_list = models.ForeignKey(to=ASPathList, on_delete=models.CASCADE, related_name="aspathlistrules")
    index = models.PositiveIntegerField()
    action = models.CharField(max_length=30, choices=ActionChoices)
    pattern = models.CharField(
        max_length=200,
    )
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.aspath_list}: {self.action} {self.pattern}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:aspathlistrule", args=[self.pk])

    def get_action_color(self):
        return ActionChoices.colors.get(self.action)

    class Meta:
        ordering = ["aspath_list", "index"]


class RoutingPolicy(NetBoxModel):
    """ """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Routing Policies"
        unique_together = ["name", "description"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:routingpolicy", args=[self.pk])


class BGPPeerGroup(NetBoxModel):
    """ """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    import_policies = models.ManyToManyField(RoutingPolicy, blank=True, related_name="group_import_policies")
    export_policies = models.ManyToManyField(RoutingPolicy, blank=True, related_name="group_export_policies")
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Peer Groups"
        unique_together = ["name", "description"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:bgppeergroup", args=[self.pk])


class BGPBase(NetBoxModel):
    """ """

    site = models.ForeignKey(
        to="dcim.Site", on_delete=models.PROTECT, related_name="%(class)s_related", blank=True, null=True
    )
    tenant = models.ForeignKey(to="tenancy.Tenant", on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=CommunityStatusChoices, default=CommunityStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(to="ipam.Role", on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        abstract = True


class Community(BGPBase):
    """ """

    value = models.CharField(max_length=64, validators=[RegexValidator(r"[\d\.\*]+:[\d\.\*]+")])

    class Meta:
        verbose_name_plural = "Communities"
        ordering = ["value"]

    def __str__(self):
        return self.value

    def get_status_color(self):
        return CommunityStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:community", args=[self.pk])


class CommunityList(NetBoxModel):
    """ """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Community Lists"
        unique_together = ["name", "description"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:communitylist", args=[self.pk])


class CommunityListRule(NetBoxModel):
    """ """

    community_list = models.ForeignKey(to=CommunityList, on_delete=models.CASCADE, related_name="commlistrules")
    action = models.CharField(max_length=30, choices=ActionChoices)
    community = models.ForeignKey(
        to=Community,
        related_name="+",
        on_delete=models.CASCADE,
    )
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.community_list}: {self.action} {self.community}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:communitylistrule", args=[self.pk])

    def get_action_color(self):
        return ActionChoices.colors.get(self.action)

    class Meta:
        ordering = ["community_list", "community"]


class PrefixList(NetBoxModel):
    """ """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    family = models.CharField(max_length=10, choices=IPAddressFamilyChoices)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Prefix Lists"
        unique_together = ["name", "description", "family"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:prefixlist", args=[self.pk])


class PrefixListRule(NetBoxModel):
    """ """

    prefix_list = models.ForeignKey(to=PrefixList, on_delete=models.CASCADE, related_name="prefrules")
    index = models.PositiveIntegerField()
    action = models.CharField(max_length=30, choices=ActionChoices)
    prefix = models.ForeignKey(
        to="ipam.Prefix",
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    prefix_custom = IPNetworkField(
        blank=True,
        null=True,
    )
    ge = models.PositiveSmallIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(128)]
    )
    le = models.PositiveSmallIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(128)]
    )
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        unique_together = ("prefix_list", "index")
        ordering = ["prefix_list", "index"]

    @property
    def network(self):
        return self.prefix_custom or self.prefix

    def __str__(self):
        return f"{self.prefix_list}: Rule {self.index}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:prefixlistrule", args=[self.pk])

    def get_action_color(self):
        return ActionChoices.colors.get(self.action)

    def clean(self):
        super().clean()
        # make sure that only one field is setted
        if self.prefix and self.prefix_custom:
            raise ValidationError({"prefix": "Cannot set both fields"})
        # at least one fields must be setted
        if self.prefix is None and self.prefix_custom is None:
            raise ValidationError({"prefix": "Cannot set both fields to Null"})


class BGPSession(NetBoxModel):
    name = models.CharField(max_length=256, blank=True, null=True)
    site = models.ForeignKey(to="dcim.Site", on_delete=models.SET_NULL, blank=True, null=True)
    tenant = models.ForeignKey(to="tenancy.Tenant", on_delete=models.PROTECT, blank=True, null=True)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    virtualmachine = models.ForeignKey(
        to="virtualization.VirtualMachine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    local_address = models.ForeignKey(to="ipam.IPAddress", on_delete=models.PROTECT, related_name="local_address")
    remote_address = models.ForeignKey(to="ipam.IPAddress", on_delete=models.PROTECT, related_name="remote_address")
    local_as = models.ForeignKey(to="ipam.ASN", on_delete=models.PROTECT, related_name="local_as")
    remote_as = models.ForeignKey(to="ipam.ASN", on_delete=models.PROTECT, related_name="remote_as")
    status = models.CharField(max_length=50, choices=SessionStatusChoices, default=SessionStatusChoices.STATUS_ACTIVE)
    description = models.CharField(max_length=200, blank=True)
    peer_group = models.ForeignKey(BGPPeerGroup, on_delete=models.SET_NULL, blank=True, null=True)
    import_policies = models.ManyToManyField(RoutingPolicy, blank=True, related_name="session_import_policies")
    export_policies = models.ManyToManyField(RoutingPolicy, blank=True, related_name="session_export_policies")
    prefix_list_in = models.ForeignKey(
        to=PrefixList, blank=True, null=True, on_delete=models.SET_NULL, related_name="session_prefix_in"
    )
    prefix_list_out = models.ForeignKey(
        to=PrefixList, blank=True, null=True, on_delete=models.SET_NULL, related_name="session_prefix_out"
    )
    comments = models.TextField(blank=True)

    # Phase 1: Session enhancements
    relationship = models.ForeignKey(
        to=Relationship,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions",
        help_text="Type of BGP relationship (e.g., transit, customer, peer)",
    )
    bfd = models.ForeignKey(
        to=BFD,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions",
        help_text="BFD configuration profile for this session",
    )
    multihop_ttl = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(255)],
        help_text="TTL for eBGP multihop (1 = directly connected)",
    )
    service_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference ID (e.g., ticket number, service ID)",
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Administrative enable/disable state",
    )

    afi_safi = None  # for future use

    class Meta:
        verbose_name_plural = "BGP Sessions"
        unique_together = [
            ["device", "local_address", "local_as", "remote_address", "remote_as"],
            ["virtualmachine", "local_address", "local_as", "remote_address", "remote_as"],
        ]
        ordering = ["name"]

    def __str__(self):
        if self.device:
            return f"{self.device}:{self.name}"
        if self.virtualmachine:
            return f"{self.virtualmachine}:{self.name}"
        return f":{self.name}"

    # def clean(self, *args, new_session=None, **kwargs):
    #    if not self.device and not self.virtualmachine:
    #        raise ValidationError(_("Either a Device or a VirtualMachine should be selected"))
    #    super().clean(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #    self.clean()
    #    super().save(*args, **kwargs)

    def get_status_color(self):
        return SessionStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:bgpsession", args=[self.pk])


class RoutingPolicyRule(NetBoxModel):
    routing_policy = models.ForeignKey(to=RoutingPolicy, on_delete=models.CASCADE, related_name="rules")
    index = models.PositiveIntegerField()
    action = models.CharField(max_length=30, choices=ActionChoices)
    description = models.CharField(max_length=500, blank=True)
    continue_entry = models.PositiveIntegerField(blank=True, null=True)
    match_community = models.ManyToManyField(to=Community, blank=True, related_name="+")
    match_community_list = models.ManyToManyField(to=CommunityList, blank=True, related_name="cmrules")
    match_aspath_list = models.ManyToManyField(to=ASPathList, blank=True, related_name="aspathrules")
    match_ip_address = models.ManyToManyField(
        to=PrefixList,
        blank=True,
        related_name="plrules",
    )
    match_ipv6_address = models.ManyToManyField(
        to=PrefixList,
        blank=True,
        related_name="plrules6",
    )
    match_custom = models.JSONField(
        blank=True,
        null=True,
    )
    set_actions = models.JSONField(
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["routing_policy", "index"]
        unique_together = ("routing_policy", "index")

    def __str__(self):
        return f"{self.routing_policy}: Rule {self.index}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:routingpolicyrule", args=[self.pk])

    def get_action_color(self):
        return ActionChoices.colors.get(self.action)

    def get_match_custom(self):
        # some kind of ckeck?
        result = {}
        if self.match_custom:
            result = self.match_custom
        return result

    @property
    def match_statements(self):
        result = {}
        # add communities
        result.update({"community": list(self.match_community.all().values_list("value", flat=True))})
        if self.match_community_list.all().exists():
            result.update({"community": list(self.match_community_list.all().values_list("name", flat=True))})
        result.update(
            {
                "ip address": [
                    str(prefix_list) for prefix_list in self.match_ip_address.all().values_list("name", flat=True)
                ]
            }
        )
        result.update(
            {
                "ipv6 address": [
                    str(prefix_list) for prefix_list in self.match_ipv6_address.all().values_list("name", flat=True)
                ]
            }
        )
        result.update({"as-path": list(self.match_aspath_list.all().values_list("name", flat=True))})

        custom_match = self.get_match_custom()
        # update community from custom
        result["community"].extend(custom_match.get("community", []))
        result["ip address"].extend(custom_match.get("ip address", []))
        result["ipv6 address"].extend(custom_match.get("ipv6 address", []))
        result["as-path"].extend(custom_match.get("as-path", []))
        # remove empty matches
        result = {k: v for k, v in result.items() if v}
        result.update(custom_match)
        return result

    @property
    def set_statements(self):
        if self.set_actions:
            return self.set_actions
        return {}
