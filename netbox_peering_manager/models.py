from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.fields import ColorField

from .choices import PeeringStatusChoices


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
        validators=[MinValueValidator(1)],
        help_text="Minutes between automatic syncs (default: 1440 = 24 hours)",
    )
    enabled = models.BooleanField(default=True, db_index=True)
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
        """Return the count of IRRPrefixListConfigs using this IRRSource."""
        return self.irr_prefix_list_configs.count()

    @prefix_list_count.setter
    def prefix_list_count(self, value):
        pass  # Allow queryset annotation to set this attribute


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
        db_index=True,
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
        db_index=True,
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
        to="netbox_routing.BGPPeerTemplate",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        help_text="Default peer template for sessions on this fabric",
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Peering Fabric"
        verbose_name_plural = "Peering Fabrics"
        constraints = [
            UniqueConstraint(
                fields=["name", "site"],
                condition=Q(site__isnull=False),
                name="unique_peeringfabric_name_site",
            ),
            UniqueConstraint(
                fields=["name"],
                condition=Q(site__isnull=True),
                name="unique_peeringfabric_name_no_site",
            ),
        ]

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
        db_index=True,
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
        db_index=True,
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


# =============================================================================
# Extension Models (linking to netbox-routing objects)
# =============================================================================


class IRRPrefixListConfig(NetBoxModel):
    """
    Extension model linking a netbox-routing PrefixList to IRR sync configuration.
    """

    prefix_list = models.OneToOneField(
        to="netbox_routing.PrefixList",
        on_delete=models.CASCADE,
        related_name="irr_config",
    )
    irr_source = models.ForeignKey(
        to="IRRSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="irr_prefix_list_configs",
        help_text="IRR source for AS-SET queries",
    )
    source_as_set = models.CharField(
        max_length=100,
        blank=True,
        help_text="AS-SET to sync from IRR (e.g., AS-HURRICANE). When set, rules are managed by IRR sync.",
    )
    sync_interval = models.PositiveIntegerField(
        default=1440,
        validators=[MinValueValidator(1)],
        help_text="Minutes between automatic syncs (default: 1440 = 24 hours)",
    )

    class Meta:
        ordering = ["prefix_list__name"]
        verbose_name = "IRR Prefix List Config"
        verbose_name_plural = "IRR Prefix List Configs"

    def __str__(self):
        return f"IRR Config: {self.prefix_list.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:irrprefixlistconfig", args=[self.pk])

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


class PeeringSession(NetBoxModel):
    """
    Extension model linking a netbox-routing BGPPeer to peering-specific metadata.
    """

    bgp_peer = models.OneToOneField(
        to="netbox_routing.BGPPeer",
        on_delete=models.PROTECT,
        related_name="peering_session",
    )
    relationship = models.ForeignKey(
        to="Relationship",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="peering_sessions",
        help_text="Type of BGP relationship (e.g., transit, customer, peer)",
    )
    peering_network = models.ForeignKey(
        to="PeeringNetwork",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="peering_sessions",
        help_text="Peering network this session operates on",
    )
    service_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference ID (e.g., ticket number, service ID)",
    )

    class Meta:
        ordering = ["bgp_peer__name"]
        verbose_name = "Peering Session"
        verbose_name_plural = "Peering Sessions"

    def __str__(self):
        return f"Peering: {self.bgp_peer.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:peeringsession", args=[self.pk])
