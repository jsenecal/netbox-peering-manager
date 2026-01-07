# ASN Extensions Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create PeerASN model to extend NetBox ASN with peering-specific fields (max-prefixes, IRR AS-SET) and PeeringDB sync.

**Architecture:** PeerASN has OneToOne relationship to ipam.ASN, storing extended peer data. BGPSession.remote_as changes to FK to PeerASN. PeeringDB sync populates max_prefixes and irr_as_set.

**Tech Stack:** Django models, NetBox plugin patterns, PeeringDB API

---

## Design Decisions

### 1. Model Approach
**Decision:** Create new PeerASN model (not custom fields on ipam.ASN)

**Rationale:**
- Full control over fields and behavior
- Clean data model with proper validation
- Easy PeeringDB sync target
- No dependency on NetBox custom field behavior

### 2. Session Relationship
**Decision:** Replace `BGPSession.remote_as` FK to point to PeerASN instead of ipam.ASN

**Rationale:**
- Clean, single source of truth
- No breaking changes (new project)
- Direct access to extended peer data from session

### 3. Local AS Handling
**Decision:** Keep `BGPSession.local_as` pointing to ipam.ASN (unchanged)

**Rationale:**
- PeerASN fields (max_prefixes, irr_as_set) are about what you *accept from* peers
- Local AS doesn't need these fields
- Simpler mental model: "PeerASN = info about external peers"

---

## PeerASN Model

```python
class PeerASN(NetBoxModel):
    """Extended ASN information for BGP peers."""

    # Core reference - OneToOne to NetBox ASN
    asn = models.OneToOneField(
        to="ipam.ASN",
        on_delete=models.CASCADE,
        related_name="peer_asn",
    )

    # Extended fields
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

    # PeeringDB integration
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

    class Meta:
        verbose_name = "Peer ASN"
        verbose_name_plural = "Peer ASNs"
        ordering = ["asn__asn"]

    def __str__(self):
        return f"AS{self.asn.asn}"

    @property
    def asn_number(self):
        """Convenience property to get the ASN number."""
        return self.asn.asn
```

---

## BGPSession Changes

```python
class BGPSession(NetBoxModel):
    # Keep local_as pointing to ipam.ASN (unchanged)
    local_as = models.ForeignKey(
        to="ipam.ASN",
        on_delete=models.PROTECT,
        related_name="local_sessions",
    )

    # Change remote_as to point to PeerASN
    remote_as = models.ForeignKey(
        to="PeerASN",
        on_delete=models.PROTECT,
        related_name="sessions",
    )
```

**Migration strategy:**
1. Create PeerASN model
2. Data migration: For each unique remote_as ASN in existing sessions, create PeerASN
3. Alter BGPSession.remote_as to FK to PeerASN

---

## PeeringDB Sync Integration

**PeeringDBClient extension:**
```python
def get_network(self, asn: int) -> dict | None:
    """Fetch network info by ASN from PeeringDB."""
    response = self._get(f"/net?asn={asn}")
    data = response.get("data", [])
    return data[0] if data else None
```

**Sync service method:**
```python
def sync_peer_asn(self, peer_asn: PeerASN) -> bool:
    """Sync PeerASN from PeeringDB."""
    network = self.client.get_network(peer_asn.asn.asn)
    if not network:
        return False

    peer_asn.peeringdb_id = network["id"]
    peer_asn.ipv4_max_prefixes = network.get("info_prefixes4")
    peer_asn.ipv6_max_prefixes = network.get("info_prefixes6")
    peer_asn.irr_as_set = network.get("irr_as_set", "")
    peer_asn.peeringdb_last_sync = timezone.now()
    peer_asn.save()
    return True
```

**Management command:** `sync_peeringdb_asn --asn 65001` or `--all`

---

## UI Components

**Views:**
- PeerASNListView, PeerASNView (detail), PeerASNEditView, PeerASNDeleteView
- PeerASNBulkEditView, PeerASNBulkDeleteView

**Table columns:**
- ASN number, ASN name (from ipam.ASN.description)
- affiliated (boolean badge)
- irr_as_set
- ipv4_max_prefixes, ipv6_max_prefixes
- PeeringDB sync status

**FilterSet:**
- affiliated (boolean)
- asn (FK filter to ipam.ASN)
- has_peeringdb (boolean - peeringdb_id is not null)

**Form:**
- ASN selector (DynamicModelChoiceField)
- All extended fields

**Navigation:**
- Add "Peer ASNs" to BGP menu section

---

## API and GraphQL

**Serializer:**
```python
class PeerASNSerializer(NetBoxModelSerializer):
    asn = NestedASNSerializer()

    class Meta:
        model = PeerASN
        fields = [
            "id", "url", "display", "asn", "affiliated",
            "irr_as_set", "ipv4_max_prefixes", "ipv6_max_prefixes",
            "peeringdb_id", "peeringdb_last_sync",
            "tags", "created", "last_updated",
        ]
```

**GraphQL Type:**
```python
@strawberry_django.type(PeerASN, fields="__all__")
class PeerASNType(NetBoxObjectType):
    asn: Annotated["ASNType", strawberry.lazy("ipam.graphql.types")]
```

---

## ConfigRenderer Context Update

Add to session serialization:
```python
{
    "peer_asn": session.remote_as.asn.asn,
    "peer_name": session.remote_as.asn.description,
    "irr_as_set": session.remote_as.irr_as_set,
    "ipv4_max_prefixes": session.remote_as.ipv4_max_prefixes,
    "ipv6_max_prefixes": session.remote_as.ipv6_max_prefixes,
}
```

**Template usage:**
```jinja2
{% if session.ipv4_max_prefixes %}
neighbor {{ session.remote_ip }} maximum-prefix {{ session.ipv4_max_prefixes }}
{% endif %}
```

---

## Implementation Tasks

1. Create PeerASN model with all fields
2. Create migration with data migration for existing sessions
3. Update BGPSession.remote_as FK to PeerASN
4. Create PeerASN forms, tables, filtersets
5. Create PeerASN views (list, detail, edit, delete, bulk)
6. Add navigation menu item
7. Create API serializer and viewset
8. Create GraphQL type
9. Add PeeringDB client get_network method
10. Create PeeringDB sync service method
11. Create management command for sync
12. Update ConfigRenderer for new fields
13. Update tests
14. Update documentation
