from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
from ipam.fields import IPNetworkField
from netbox.models import NetBoxModel
from utilities.fields import ColorField

from .choices import (
    ActionChoices,
    CommunityStatusChoices,
    PeeringStatusChoices,
    SessionStatusChoices,
)
from .validators import validate_community


class IRRSource(NetBoxModel):
    """
    Configuration for an IRR query source (fastbgpq4 instance).
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    url = models.URLField(help_text="fastbgpq4 API base URL (e.g., http://fastbgpq4:8000)")
    sources = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated IRR sources (e.g., RIPE,RADB,ARIN). Leave blank for default.",
    )
    cache_ttl = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Override default cache TTL in seconds",
    )
    sync_interval = models.PositiveIntegerField(
        default=1440,
        help_text="Minutes between automatic syncs (default: 1440 = 24 hours)",
    )
    enabled = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "IRR Source"
        verbose_name_plural = "IRR Sources"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:irrsource", args=[self.pk])

    @property
    def prefix_list_count(self):
        """Return the count of PrefixLists using this IRRSource."""
        return self.prefix_lists.count()


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


class PeerASN(NetBoxModel):
    """
    Extended ASN information for BGP peers.
    Stores peering-specific data that doesn't belong on the core NetBox ASN model.
    """

    asn = models.OneToOneField(
        to="ipam.ASN",
        on_delete=models.CASCADE,
        related_name="peer_asn",
        help_text="NetBox ASN this extends",
    )
    affiliated = models.BooleanField(
        default=False,
        help_text="ASN is operated by your organization (subsidiary, partner)",
    )
    irr_as_set = models.CharField(
        max_length=100,
        blank=True,
        help_text="IRR AS-SET name, e.g., AS-CUSTOMER or RIPE::AS-EXAMPLE",
    )
    ipv4_max_prefixes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum IPv4 prefixes to accept",
    )
    ipv6_max_prefixes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum IPv6 prefixes to accept",
    )
    peeringdb_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="PeeringDB Network ID",
    )
    peeringdb_last_sync = models.DateTimeField(
        null=True,
        blank=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["asn__asn"]
        verbose_name = "Peer ASN"
        verbose_name_plural = "Peer ASNs"

    def __str__(self):
        return f"AS{self.asn.asn}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peerasn", args=[self.pk])

    @property
    def asn_number(self):
        """Convenience property to get the ASN number."""
        return self.asn.asn

    @property
    def name(self):
        """Get the ASN description/name from the linked ASN."""
        return self.asn.description or f"AS{self.asn.asn}"


class PeeringFabricType(NetBoxModel):
    """
    Organizational model for classifying peering fabric types.
    Examples: Internet Exchange, Cloud Exchange, Private Peering LAN.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    color = ColorField(default="9e9e9e")

    class Meta:
        ordering = ["name"]
        verbose_name = "Peering Fabric Type"
        verbose_name_plural = "Peering Fabric Types"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peeringfabrictype", args=[self.pk])


class PeeringFabric(NetBoxModel):
    """
    Represents a shared peering environment such as an Internet Exchange,
    cloud exchange, or private peering LAN.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    type = models.ForeignKey(
        to="PeeringFabricType",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fabrics",
    )
    status = models.CharField(
        max_length=50,
        choices=PeeringStatusChoices,
        default=PeeringStatusChoices.STATUS_ACTIVE,
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="peering_fabrics",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="peering_fabrics",
    )
    peer_group = models.ForeignKey(
        to="BGPPeerGroup",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fabrics",
        help_text="Default peer group for sessions on this fabric",
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "site"]
        verbose_name = "Peering Fabric"
        verbose_name_plural = "Peering Fabrics"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peeringfabric", args=[self.pk])

    def get_status_color(self):
        return PeeringStatusChoices.colors.get(self.status)


class PeeringNetwork(NetBoxModel):
    """
    A specific peering LAN within a fabric. A fabric may have multiple networks
    (e.g., production peering, GRX service, reseller VLAN).
    """

    fabric = models.ForeignKey(
        to="PeeringFabric",
        on_delete=models.CASCADE,
        related_name="networks",
    )
    name = models.CharField(max_length=100)
    prefix = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.PROTECT,
        related_name="peering_networks",
    )
    vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="peering_networks",
    )
    status = models.CharField(
        max_length=50,
        choices=PeeringStatusChoices,
        default=PeeringStatusChoices.STATUS_ACTIVE,
    )
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["fabric", "name"]
        unique_together = ["fabric", "name"]
        verbose_name = "Peering Network"
        verbose_name_plural = "Peering Networks"

    def __str__(self):
        return f"{self.fabric.name}: {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peeringnetwork", args=[self.pk])

    def get_status_color(self):
        return PeeringStatusChoices.colors.get(self.status)


class PeeringFabricPeeringDB(models.Model):
    """PeeringDB metadata for a PeeringFabric - populated by sync."""

    fabric = models.OneToOneField(
        to="PeeringFabric",
        on_delete=models.CASCADE,
        related_name="peeringdb",
    )
    ix_id = models.PositiveIntegerField(
        unique=True,
        help_text="PeeringDB IX ID",
    )
    name = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code",
    )
    website = models.URLField(blank=True)
    tech_email = models.EmailField(blank=True)
    last_sync = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PeeringDB Info"
        verbose_name_plural = "PeeringDB Info"

    def __str__(self):
        return f"PeeringDB:{self.ix_id} ({self.name})"


class PeeringNetworkPeeringDB(models.Model):
    """PeeringDB IXLAN metadata for a PeeringNetwork - populated by sync."""

    network = models.OneToOneField(
        to="PeeringNetwork",
        on_delete=models.CASCADE,
        related_name="peeringdb",
    )
    ixlan_id = models.PositiveIntegerField(
        unique=True,
        help_text="PeeringDB IXLAN ID",
    )
    name = models.CharField(max_length=200, blank=True)
    mtu = models.PositiveIntegerField(null=True, blank=True)
    rs_asn = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="Route server ASN",
    )
    dot1q_support = models.BooleanField(default=False)
    last_sync = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PeeringDB IXLAN Info"
        verbose_name_plural = "PeeringDB IXLAN Info"

    def __str__(self):
        return f"PeeringDB IXLAN:{self.ixlan_id}"


class PeeringDBPeer(models.Model):
    """
    Cached peer presence at a fabric - refreshed on sync.

    Each record represents a unique network connection at an exchange,
    identified by the combination of fabric, ASN, and IP addresses.
    At least one IP address (IPv4 or IPv6) must be provided.
    """

    fabric = models.ForeignKey(
        to="PeeringFabric",
        on_delete=models.CASCADE,
        related_name="peeringdb_peers",
    )
    asn = models.PositiveBigIntegerField()
    name = models.CharField(max_length=200)
    ipv4_addr = models.GenericIPAddressField(
        protocol="IPv4",
        null=True,
        blank=True,
    )
    ipv6_addr = models.GenericIPAddressField(
        protocol="IPv6",
        null=True,
        blank=True,
    )
    is_rs_peer = models.BooleanField(
        default=False,
        help_text="Route server peer",
    )
    speed = models.PositiveIntegerField(
        default=0,
        help_text="Port speed in Mbps",
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Note: unique_together with nullable fields allows NULL duplicates in SQL.
        # The clean() method ensures at least one IP is always present,
        # making the constraint effective.
        unique_together = ["fabric", "asn", "ipv4_addr", "ipv6_addr"]
        verbose_name = "PeeringDB Peer"
        verbose_name_plural = "PeeringDB Peers"
        ordering = ["asn", "name"]

    def __str__(self):
        return f"AS{self.asn} - {self.name}"

    def clean(self):
        super().clean()
        if not self.ipv4_addr and not self.ipv6_addr:
            msg = "At least one IP address (IPv4 or IPv6) must be provided."
            raise ValidationError(msg)


class PeeringConnection(NetBoxModel):
    """
    Your router's attachment to a peering network. Leverages NetBox's Interface
    model for IP addresses, MAC, and VLAN assignments.
    """

    peering_network = models.ForeignKey(
        to="PeeringNetwork",
        on_delete=models.CASCADE,
        related_name="connections",
    )
    interface = models.ForeignKey(
        to="dcim.Interface",
        on_delete=models.PROTECT,
        related_name="peering_connections",
    )
    status = models.CharField(
        max_length=50,
        choices=PeeringStatusChoices,
        default=PeeringStatusChoices.STATUS_ACTIVE,
    )
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["peering_network", "interface"]
        unique_together = ["peering_network", "interface"]
        verbose_name = "Peering Connection"
        verbose_name_plural = "Peering Connections"

    def __str__(self):
        return f"{self.peering_network}: {self.interface}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peeringconnection", args=[self.pk])

    def get_status_color(self):
        return PeeringStatusChoices.colors.get(self.status)

    @property
    def device(self):
        """Return the device from the interface."""
        return self.interface.device

    @property
    def ip_addresses(self):
        """Return IP addresses on the interface within the peering network's prefix."""
        from ipam.models import IPAddress

        return IPAddress.objects.filter(
            assigned_object_type__model="interface",
            assigned_object_id=self.interface.id,
            address__net_contained=self.peering_network.prefix.prefix,
        )


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

    # Phase 4: Policy enhancements
    weight = models.PositiveIntegerField(
        default=0,
        help_text="Higher weight policies are evaluated first",
    )
    address_family = models.PositiveSmallIntegerField(
        choices=CoreIPAddressFamilyChoices,
        blank=True,
        null=True,
        help_text="Restrict policy to specific address family",
    )

    class Meta:
        verbose_name_plural = "Routing Policies"
        unique_together = ["name", "description"]
        ordering = ["-weight", "name"]

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

    value = models.CharField(max_length=64, validators=[validate_community])

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
    family = models.PositiveSmallIntegerField(choices=CoreIPAddressFamilyChoices)
    comments = models.TextField(blank=True)
    source_as_set = models.CharField(
        max_length=100,
        blank=True,
        help_text="AS-SET to sync from IRR (e.g., AS-HURRICANE). When set, rules are managed by IRR sync.",
    )
    irr_source = models.ForeignKey(
        to="IRRSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prefix_lists",
        help_text="IRR source for AS-SET queries",
    )

    class Meta:
        verbose_name_plural = "Prefix Lists"
        unique_together = ["name", "description", "family"]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:prefixlist", args=[self.pk])

    def clean(self):
        super().clean()
        if self.source_as_set and not self.irr_source:
            raise ValidationError({"irr_source": "IRR source is required when source_as_set is specified."})
        if self.irr_source and not self.source_as_set:
            raise ValidationError({"source_as_set": "Source AS-SET is required when IRR source is specified."})

    @property
    def is_irr_managed(self):
        """Return True if this PrefixList is managed by IRR sync."""
        return bool(self.source_as_set and self.irr_source)


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
    remote_as = models.ForeignKey(
        to="PeerASN",
        on_delete=models.PROTECT,
        related_name="sessions",
        help_text="Peer ASN for this session",
    )
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

    # Phase 2: Peering fabric support
    peering_network = models.ForeignKey(
        to="PeeringNetwork",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions",
        help_text="Peering network this session operates on (for fabric-based sessions)",
    )

    # Phase 4: Session security
    password = models.CharField(
        max_length=256,
        blank=True,
        help_text="MD5 authentication password for this session",
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
