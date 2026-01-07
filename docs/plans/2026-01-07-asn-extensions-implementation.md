# ASN Extensions Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create PeerASN model extending NetBox ASN with peering-specific fields, update BGPSession to use it, and add PeeringDB sync.

**Architecture:** PeerASN has OneToOne to ipam.ASN with extended fields. BGPSession.remote_as changes to FK to PeerASN. Migration creates PeerASN records for existing sessions.

**Tech Stack:** Django models, NetBox plugin patterns, PeeringDB API

---

## Task 1: Create PeerASN Model

**Files:**
- Modify: `netbox_peering_manager/models.py`

**Step 1: Add PeerASN model after Relationship class**

Add this model definition after the `Relationship` class (around line 82):

```python
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
```

**Step 2: Update model imports in __init__ section**

The model will be auto-discovered. Ensure it's exported in `models.py` `__all__` if used.

**Step 3: Run makemigrations**

Run: `python /opt/netbox/netbox/manage.py makemigrations netbox_peering_manager --name create_peerasn`
Expected: Migration file created

**Step 4: Run migrate**

Run: `python /opt/netbox/netbox/manage.py migrate netbox_peering_manager`
Expected: Migration applied

**Step 5: Commit**

```bash
git add netbox_peering_manager/models.py netbox_peering_manager/migrations/
git commit -m "feat: add PeerASN model"
```

---

## Task 2: Update BGPSession to Use PeerASN

**Files:**
- Modify: `netbox_peering_manager/models.py`
- Create: Migration with data migration

**Step 1: Change remote_as FK in BGPSession**

Find the `remote_as` field (around line 738) and change:

```python
# Before:
remote_as = models.ForeignKey(to="ipam.ASN", on_delete=models.PROTECT, related_name="remote_as")

# After:
remote_as = models.ForeignKey(
    to="PeerASN",
    on_delete=models.PROTECT,
    related_name="sessions",
    help_text="Peer ASN for this session",
)
```

**Step 2: Update unique_together constraint**

The constraint references `remote_as` which still works since it's an FK.

**Step 3: Create migration with data migration**

Run: `python /opt/netbox/netbox/manage.py makemigrations netbox_peering_manager --name update_bgpsession_remote_as`

Then edit the migration to add data migration:

```python
from django.db import migrations, models
import django.db.models.deletion


def create_peer_asns_for_sessions(apps, schema_editor):
    """Create PeerASN records for each unique remote_as in BGPSession."""
    BGPSession = apps.get_model("netbox_peering_manager", "BGPSession")
    PeerASN = apps.get_model("netbox_peering_manager", "PeerASN")

    # Get unique ASN IDs used as remote_as
    asn_ids = BGPSession.objects.values_list("remote_as_id", flat=True).distinct()

    for asn_id in asn_ids:
        if asn_id and not PeerASN.objects.filter(asn_id=asn_id).exists():
            PeerASN.objects.create(asn_id=asn_id)


def reverse_migration(apps, schema_editor):
    """No-op for reverse - keep PeerASN records."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_peering_manager", "XXXX_create_peerasn"),  # Previous migration
    ]

    operations = [
        # First create PeerASN for each existing remote_as
        migrations.RunPython(create_peer_asns_for_sessions, reverse_migration),

        # Then alter the field
        migrations.AlterField(
            model_name="bgpsession",
            name="remote_as",
            field=models.ForeignKey(
                help_text="Peer ASN for this session",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sessions",
                to="netbox_peering_manager.peerasn",
            ),
        ),
    ]
```

**Step 4: Run migrate**

Run: `python /opt/netbox/netbox/manage.py migrate netbox_peering_manager`

**Step 5: Commit**

```bash
git add netbox_peering_manager/models.py netbox_peering_manager/migrations/
git commit -m "feat: update BGPSession.remote_as to use PeerASN"
```

---

## Task 3: Create PeerASN Forms

**Files:**
- Modify: `netbox_peering_manager/forms.py`

**Step 1: Add imports**

Add `PeerASN` to the model imports.

**Step 2: Add PeerASN forms after Relationship forms**

```python
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
            "asn", "affiliated", "irr_as_set",
            "ipv4_max_prefixes", "ipv6_max_prefixes",
            "peeringdb_id", "tags", "comments",
        ]


class PeerASNFilterForm(NetBoxModelFilterSetForm):
    model = PeerASN
    q = forms.CharField(required=False, label="Search")
    affiliated = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ("", "---------"),
            ("true", "Yes"),
            ("false", "No"),
        ]),
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
            "asn", "affiliated", "irr_as_set",
            "ipv4_max_prefixes", "ipv6_max_prefixes",
            "peeringdb_id", "tags",
        ]
```

**Step 3: Update BGPSessionForm to use PeerASN for remote_as**

Find the BGPSessionForm and update the remote_as field:

```python
# Change from:
remote_as = DynamicModelChoiceField(queryset=ASN.objects.all())

# To:
remote_as = DynamicModelChoiceField(
    queryset=PeerASN.objects.all(),
    help_text="Peer ASN for this session",
)
```

**Step 4: Verify tests pass**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager -v 2 --parallel`

**Step 5: Commit**

```bash
git add netbox_peering_manager/forms.py
git commit -m "feat: add PeerASN forms and update BGPSession form"
```

---

## Task 4: Create PeerASN Table and FilterSet

**Files:**
- Modify: `netbox_peering_manager/tables.py`
- Modify: `netbox_peering_manager/filtersets.py`

**Step 1: Add PeerASNTable**

```python
class PeerASNTable(NetBoxTable):
    asn = tables.Column(linkify=True, verbose_name="ASN")
    affiliated = BooleanColumn()
    ipv4_max_prefixes = tables.Column(verbose_name="IPv4 Max Prefixes")
    ipv6_max_prefixes = tables.Column(verbose_name="IPv6 Max Prefixes")
    peeringdb_id = tables.Column(verbose_name="PeeringDB ID")
    session_count = tables.Column(
        verbose_name="Sessions",
        accessor="sessions__count",
        orderable=False,
    )
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = PeerASN
        fields = (
            "pk", "id", "asn", "affiliated", "irr_as_set",
            "ipv4_max_prefixes", "ipv6_max_prefixes",
            "peeringdb_id", "session_count", "tags",
        )
        default_columns = (
            "asn", "affiliated", "irr_as_set",
            "ipv4_max_prefixes", "ipv6_max_prefixes", "session_count",
        )
```

**Step 2: Add PeerASNFilterSet**

```python
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

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(asn__asn__icontains=value) |
            Q(asn__description__icontains=value) |
            Q(irr_as_set__icontains=value)
        )
```

**Step 3: Add imports for PeerASN model**

**Step 4: Commit**

```bash
git add netbox_peering_manager/tables.py netbox_peering_manager/filtersets.py
git commit -m "feat: add PeerASN table and filterset"
```

---

## Task 5: Create PeerASN Views

**Files:**
- Modify: `netbox_peering_manager/views.py`

**Step 1: Add PeerASN views**

```python
# =============================================================================
# Peer ASN Views
# =============================================================================


@register_model_view(PeerASN)
class PeerASNView(generic.ObjectView):
    queryset = PeerASN.objects.all()

    def get_extra_context(self, request, instance):
        sessions = BGPSession.objects.filter(remote_as=instance)
        sessions_table = BGPSessionTable(sessions)
        sessions_table.configure(request)
        return {
            "sessions_table": sessions_table,
        }


class PeerASNListView(generic.ObjectListView):
    queryset = PeerASN.objects.annotate(
        session_count=Count("sessions")
    )
    table = PeerASNTable
    filterset = PeerASNFilterSet
    filterset_form = PeerASNFilterForm


@register_model_view(PeerASN, "edit")
class PeerASNEditView(generic.ObjectEditView):
    queryset = PeerASN.objects.all()
    form = PeerASNForm


@register_model_view(PeerASN, "delete")
class PeerASNDeleteView(generic.ObjectDeleteView):
    queryset = PeerASN.objects.all()


class PeerASNBulkEditView(generic.BulkEditView):
    queryset = PeerASN.objects.all()
    filterset = PeerASNFilterSet
    table = PeerASNTable
    form = PeerASNBulkEditForm


class PeerASNBulkDeleteView(generic.BulkDeleteView):
    queryset = PeerASN.objects.all()
    filterset = PeerASNFilterSet
    table = PeerASNTable


class PeerASNBulkImportView(generic.BulkImportView):
    queryset = PeerASN.objects.all()
    model_form = PeerASNImportForm
```

**Step 2: Add imports**

Add PeerASN model and related forms/tables/filtersets to imports.

**Step 3: Commit**

```bash
git add netbox_peering_manager/views.py
git commit -m "feat: add PeerASN views"
```

---

## Task 6: Add PeerASN URL Patterns and Navigation

**Files:**
- Modify: `netbox_peering_manager/urls.py`
- Modify: `netbox_peering_manager/navigation.py`

**Step 1: Add URL patterns**

```python
# Peer ASN URLs
path("peer-asn/", views.PeerASNListView.as_view(), name="peerasn_list"),
path("peer-asn/add/", views.PeerASNEditView.as_view(), name="peerasn_add"),
path("peer-asn/import/", views.PeerASNBulkImportView.as_view(), name="peerasn_import"),
path("peer-asn/edit/", views.PeerASNBulkEditView.as_view(), name="peerasn_bulk_edit"),
path("peer-asn/delete/", views.PeerASNBulkDeleteView.as_view(), name="peerasn_bulk_delete"),
path("peer-asn/<int:pk>/", views.PeerASNView.as_view(), name="peerasn"),
path("peer-asn/<int:pk>/edit/", views.PeerASNEditView.as_view(), name="peerasn_edit"),
path("peer-asn/<int:pk>/delete/", views.PeerASNDeleteView.as_view(), name="peerasn_delete"),
```

**Step 2: Add navigation menu item**

Add to the menu items:

```python
PluginMenuItem(
    link="plugins:netbox_peering_manager:peerasn_list",
    link_text="Peer ASNs",
    permissions=["netbox_peering_manager.view_peerasn"],
),
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/urls.py netbox_peering_manager/navigation.py
git commit -m "feat: add PeerASN URLs and navigation"
```

---

## Task 7: Create PeerASN API Serializer and ViewSet

**Files:**
- Modify: `netbox_peering_manager/api/serializers.py`
- Modify: `netbox_peering_manager/api/views.py`
- Modify: `netbox_peering_manager/api/urls.py`

**Step 1: Add PeerASNSerializer**

```python
class PeerASNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_peering_manager-api:peerasn-detail"
    )
    asn = NestedASNSerializer()
    session_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PeerASN
        fields = [
            "id", "url", "display", "asn", "affiliated",
            "irr_as_set", "ipv4_max_prefixes", "ipv6_max_prefixes",
            "peeringdb_id", "peeringdb_last_sync", "session_count",
            "comments", "tags", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "asn", "affiliated"]
```

**Step 2: Add PeerASNViewSet**

```python
class PeerASNViewSet(NetBoxModelViewSet):
    queryset = PeerASN.objects.annotate(session_count=Count("sessions"))
    serializer_class = PeerASNSerializer
    filterset_class = PeerASNFilterSet
```

**Step 3: Register router**

```python
router.register("peer-asn", PeerASNViewSet)
```

**Step 4: Update BGPSessionSerializer**

Update the `remote_as` field to use nested PeerASNSerializer.

**Step 5: Commit**

```bash
git add netbox_peering_manager/api/
git commit -m "feat: add PeerASN API serializer and viewset"
```

---

## Task 8: Create PeerASN GraphQL Type

**Files:**
- Modify: `netbox_peering_manager/graphql/types.py`

**Step 1: Add PeerASNType**

```python
@strawberry_django.type(PeerASN, fields="__all__")
class PeerASNType(NetBoxObjectType):
    asn: Annotated["ASNType", strawberry.lazy("ipam.graphql.types")]
```

**Step 2: Add to schema query**

```python
peer_asn: PeerASNType = strawberry_django.field()
peer_asn_list: list[PeerASNType] = strawberry_django.field()
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/graphql/
git commit -m "feat: add PeerASN GraphQL type"
```

---

## Task 9: Add PeeringDB Network Sync

**Files:**
- Modify: `netbox_peering_manager/services/peeringdb.py`
- Modify: `netbox_peering_manager/services/peeringdb_sync.py`

**Step 1: Add get_network method to PeeringDBClient**

```python
def get_network(self, asn: int) -> dict | None:
    """Fetch network info by ASN from PeeringDB.

    Args:
        asn: The AS number to look up.

    Returns:
        Network data dict or None if not found.
    """
    response = self._get(f"/net?asn={asn}")
    data = response.get("data", [])
    return data[0] if data else None
```

**Step 2: Add sync_peer_asn method to PeeringDBSyncService**

```python
def sync_peer_asn(self, peer_asn: PeerASN) -> bool:
    """Sync PeerASN data from PeeringDB.

    Args:
        peer_asn: The PeerASN to sync.

    Returns:
        True if sync successful, False otherwise.
    """
    network = self.client.get_network(peer_asn.asn.asn)
    if not network:
        logger.warning(f"No PeeringDB network found for AS{peer_asn.asn.asn}")
        return False

    peer_asn.peeringdb_id = network["id"]
    peer_asn.ipv4_max_prefixes = network.get("info_prefixes4")
    peer_asn.ipv6_max_prefixes = network.get("info_prefixes6")
    peer_asn.irr_as_set = network.get("irr_as_set", "")
    peer_asn.peeringdb_last_sync = timezone.now()
    peer_asn.save()

    logger.info(f"Synced PeerASN {peer_asn} from PeeringDB")
    return True
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/services/
git commit -m "feat: add PeeringDB network sync for PeerASN"
```

---

## Task 10: Update ConfigRenderer for PeerASN Fields

**Files:**
- Modify: `netbox_peering_manager/services/config_renderer.py`

**Step 1: Update session serialization**

In `_serialize_session()`, update the peer ASN fields:

```python
# Change from:
"peer_asn": session.remote_as.asn if session.remote_as else None,

# To:
"peer_asn": session.remote_as.asn.asn if session.remote_as else None,
"peer_name": session.remote_as.name if session.remote_as else None,
"irr_as_set": session.remote_as.irr_as_set if session.remote_as else None,
"ipv4_max_prefixes": session.remote_as.ipv4_max_prefixes if session.remote_as else None,
"ipv6_max_prefixes": session.remote_as.ipv6_max_prefixes if session.remote_as else None,
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/services/config_renderer.py
git commit -m "feat: add PeerASN fields to ConfigRenderer context"
```

---

## Task 11: Create PeerASN Templates

**Files:**
- Create: `netbox_peering_manager/templates/netbox_peering_manager/peerasn.html`
- Create: `netbox_peering_manager/templates/netbox_peering_manager/peerasn_list.html`

**Step 1: Create detail template**

Create `peerasn.html` following the pattern of other detail templates in the plugin.

**Step 2: Create list template (optional - may use generic)**

**Step 3: Commit**

```bash
git add netbox_peering_manager/templates/
git commit -m "feat: add PeerASN templates"
```

---

## Task 12: Update Tests

**Files:**
- Modify: `netbox_peering_manager/tests/test_api.py`
- Modify: `netbox_peering_manager/tests/test_models.py` (if exists)

**Step 1: Add PeerASN API tests**

```python
class PeerASNAPITestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = PeerASN
    view_namespace = "plugins-api:netbox_peering_manager"
    brief_fields = ["id", "url", "display", "asn", "affiliated"]

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name="Test RIR API", slug="test-rir-api")
        asns = [
            ASN.objects.create(asn=65100, rir=rir),
            ASN.objects.create(asn=65101, rir=rir),
            ASN.objects.create(asn=65102, rir=rir),
            ASN.objects.create(asn=65103, rir=rir),
            ASN.objects.create(asn=65104, rir=rir),
            ASN.objects.create(asn=65105, rir=rir),
        ]
        PeerASN.objects.create(asn=asns[0])
        PeerASN.objects.create(asn=asns[1])
        PeerASN.objects.create(asn=asns[2])

        cls.create_data = [
            {"asn": asns[3].pk},
            {"asn": asns[4].pk},
            {"asn": asns[5].pk},
        ]
        cls.bulk_update_data = {"affiliated": True}
```

**Step 2: Update BGPSession tests**

Update tests that create BGPSession to use PeerASN for remote_as.

**Step 3: Run tests**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager -v 2 --parallel`

**Step 4: Commit**

```bash
git add netbox_peering_manager/tests/
git commit -m "test: add PeerASN tests and update BGPSession tests"
```

---

## Task 13: Update Documentation

**Files:**
- Modify: `docs/FEATURE_GAP_ANALYSIS.md`

**Step 1: Mark Phase 6 as completed**

Update the Phase 6 section with implementation details and mark tasks as complete.

**Step 2: Update Feature Comparison Matrix**

Update ASN Management from "Partial" to "Implemented".

**Step 3: Commit**

```bash
git add docs/FEATURE_GAP_ANALYSIS.md
git commit -m "docs: mark Phase 6 ASN Extensions as completed"
```

---

## Task 14: Final Verification

**Step 1: Run full test suite**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager -v 2 --parallel`

**Step 2: Push to origin**

Run: `git push origin develop`

---

## Summary

**Files created:**
- `netbox_peering_manager/templates/netbox_peering_manager/peerasn.html`
- Migration files

**Files modified:**
- `netbox_peering_manager/models.py` - Add PeerASN, update BGPSession
- `netbox_peering_manager/forms.py` - Add PeerASN forms
- `netbox_peering_manager/tables.py` - Add PeerASNTable
- `netbox_peering_manager/filtersets.py` - Add PeerASNFilterSet
- `netbox_peering_manager/views.py` - Add PeerASN views
- `netbox_peering_manager/urls.py` - Add PeerASN URLs
- `netbox_peering_manager/navigation.py` - Add menu item
- `netbox_peering_manager/api/serializers.py` - Add PeerASNSerializer
- `netbox_peering_manager/api/views.py` - Add PeerASNViewSet
- `netbox_peering_manager/api/urls.py` - Register router
- `netbox_peering_manager/graphql/types.py` - Add PeerASNType
- `netbox_peering_manager/services/peeringdb.py` - Add get_network
- `netbox_peering_manager/services/peeringdb_sync.py` - Add sync_peer_asn
- `netbox_peering_manager/services/config_renderer.py` - Update context
- `netbox_peering_manager/tests/test_api.py` - Add tests
- `docs/FEATURE_GAP_ANALYSIS.md` - Update status
