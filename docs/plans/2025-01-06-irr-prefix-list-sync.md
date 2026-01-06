# IRR Prefix List Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically generate PrefixList rules from AS-SETs by integrating with fastbgpq4.

**Architecture:** Add `IRRSource` model for fastbgpq4 configuration, extend `PrefixList` with AS-SET fields, implement sync jobs using NetBox's JobRunner framework.

**Tech Stack:** NetBox JobRunner, httpx async HTTP client, fastbgpq4 API

---

## Task 1: Add IRRSource Model

**Files:**
- Modify: `netbox_peering_manager/models.py`
- Modify: `netbox_peering_manager/choices.py`

**Step 1: Add model to models.py**

Add after the existing imports and before `class Relationship`:

```python
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
```

**Step 2: Add fields to PrefixList model**

Find the `PrefixList` class and add these fields after `comments`:

```python
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
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/models.py
git commit -m "feat: add IRRSource model and PrefixList IRR fields"
```

---

## Task 2: Create Migration

**Files:**
- Create: `netbox_peering_manager/migrations/0040_irr_source.py`

**Step 1: Create migration file**

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_peering_manager", "0039_peering_fabric"),
    ]

    operations = [
        migrations.CreateModel(
            name="IRRSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=None)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("url", models.URLField(help_text="fastbgpq4 API base URL (e.g., http://fastbgpq4:8000)")),
                ("sources", models.CharField(blank=True, help_text="Comma-separated IRR sources (e.g., RIPE,RADB,ARIN). Leave blank for default.", max_length=200)),
                ("cache_ttl", models.PositiveIntegerField(blank=True, help_text="Override default cache TTL in seconds", null=True)),
                ("sync_interval", models.PositiveIntegerField(default=1440, help_text="Minutes between automatic syncs (default: 1440 = 24 hours)")),
                ("enabled", models.BooleanField(default=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
                ("tags", models.ManyToManyField(blank=True, related_name="+", to="extras.tag")),
            ],
            options={
                "verbose_name": "IRR Source",
                "verbose_name_plural": "IRR Sources",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="prefixlist",
            name="source_as_set",
            field=models.CharField(blank=True, help_text="AS-SET to sync from IRR (e.g., AS-HURRICANE). When set, rules are managed by IRR sync.", max_length=100),
        ),
        migrations.AddField(
            model_name="prefixlist",
            name="irr_source",
            field=models.ForeignKey(blank=True, help_text="IRR source for AS-SET queries", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prefix_lists", to="netbox_peering_manager.irrsource"),
        ),
    ]
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/migrations/0040_irr_source.py
git commit -m "feat: add migration for IRRSource and PrefixList IRR fields"
```

---

## Task 3: Add IRRSource FilterSet

**Files:**
- Modify: `netbox_peering_manager/filtersets.py`

**Step 1: Add import for IRRSource**

Find the model imports and add `IRRSource`:

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
```

**Step 2: Add IRRSourceFilterSet class**

Add before `PrefixListFilterSet`:

```python
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
```

**Step 3: Update PrefixListFilterSet to include new fields**

Add `source_as_set` and `irr_source` to the fields tuple in `PrefixListFilterSet.Meta`:

```python
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
```

**Step 4: Commit**

```bash
git add netbox_peering_manager/filtersets.py
git commit -m "feat: add IRRSource filterset and update PrefixList filterset"
```

---

## Task 4: Add IRRSource Table

**Files:**
- Modify: `netbox_peering_manager/tables.py`

**Step 1: Add import for IRRSource**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
```

**Step 2: Add IRRSourceTable class**

Add before `PrefixListTable`:

```python
class IRRSourceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    prefix_lists = columns.LinkedCountColumn(
        viewname="plugins:netbox_peering_manager:prefixlist_list",
        url_params={"irr_source_id": "pk"},
        verbose_name="Prefix Lists",
    )
    tags = columns.TagColumn(url_name="plugins:netbox_peering_manager:irrsource_list")

    class Meta(NetBoxTable.Meta):
        model = IRRSource
        fields = (
            "pk",
            "id",
            "name",
            "url",
            "sources",
            "sync_interval",
            "enabled",
            "prefix_lists",
            "tags",
        )
        default_columns = ("name", "url", "sync_interval", "enabled", "prefix_lists")
```

**Step 3: Update PrefixListTable to show IRR status**

Add columns to `PrefixListTable`:

```python
class PrefixListTable(NetBoxTable):
    name = tables.Column(linkify=True)
    source_as_set = tables.Column(verbose_name="AS-SET")
    irr_source = tables.Column(linkify=True, verbose_name="IRR Source")
    tags = columns.TagColumn(url_name="plugins:netbox_peering_manager:prefixlist_list")

    class Meta(NetBoxTable.Meta):
        model = PrefixList
        fields = (
            "pk",
            "id",
            "name",
            "family",
            "source_as_set",
            "irr_source",
            "description",
            "tags",
        )
        default_columns = ("name", "family", "source_as_set", "description")
```

**Step 4: Commit**

```bash
git add netbox_peering_manager/tables.py
git commit -m "feat: add IRRSource table and update PrefixList table"
```

---

## Task 5: Add IRRSource Forms

**Files:**
- Modify: `netbox_peering_manager/forms.py`

**Step 1: Add imports**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
```

**Step 2: Add IRRSource forms**

Add before `PrefixListForm`:

```python
#
# IRRSource
#


class IRRSourceForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        model = IRRSource
        fields = (
            "name",
            "slug",
            "url",
            "sources",
            "cache_ttl",
            "sync_interval",
            "enabled",
            "description",
            "comments",
            "tags",
        )


class IRRSourceFilterForm(NetBoxModelFilterSetForm):
    model = IRRSource
    name = forms.CharField(required=False)
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )
    tag = TagFilterField(model)


class IRRSourceBulkEditForm(NetBoxModelBulkEditForm):
    model = IRRSource
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect())
    sync_interval = forms.IntegerField(required=False, min_value=1)
    description = forms.CharField(max_length=200, required=False)

    nullable_fields = ("description",)


class IRRSourceImportForm(NetBoxModelImportForm):
    class Meta:
        model = IRRSource
        fields = (
            "name",
            "slug",
            "url",
            "sources",
            "cache_ttl",
            "sync_interval",
            "enabled",
            "description",
            "comments",
            "tags",
        )
```

**Step 3: Update PrefixListForm to include IRR fields**

Find `PrefixListForm` and update it:

```python
class PrefixListForm(NetBoxModelForm):
    irr_source = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label="IRR Source",
    )

    class Meta:
        model = PrefixList
        fields = (
            "name",
            "description",
            "family",
            "source_as_set",
            "irr_source",
            "comments",
            "tags",
        )
        help_texts = {
            "source_as_set": "When set, prefix rules are automatically synced from IRR. Existing rules will be replaced.",
        }
```

**Step 4: Update PrefixListFilterForm**

```python
class PrefixListFilterForm(NetBoxModelFilterSetForm):
    model = PrefixList
    name = forms.CharField(required=False)
    family = forms.ChoiceField(
        choices=add_blank_choice(IPAddressFamilyChoices),
        required=False,
    )
    source_as_set = forms.CharField(required=False, label="Source AS-SET")
    irr_source_id = DynamicModelChoiceField(
        queryset=IRRSource.objects.all(),
        required=False,
        label="IRR Source",
    )
    tag = TagFilterField(model)
```

**Step 5: Commit**

```bash
git add netbox_peering_manager/forms.py
git commit -m "feat: add IRRSource forms and update PrefixList forms"
```

---

## Task 6: Add IRRSource Views

**Files:**
- Modify: `netbox_peering_manager/views.py`

**Step 1: Add imports**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
from netbox_peering_manager.tables import (
    # ... existing imports ...
    IRRSourceTable,
)
from netbox_peering_manager.filtersets import (
    # ... existing imports ...
    IRRSourceFilterSet,
)
from netbox_peering_manager.forms import (
    # ... existing imports ...
    IRRSourceForm,
    IRRSourceFilterForm,
    IRRSourceBulkEditForm,
    IRRSourceImportForm,
)
```

**Step 2: Add IRRSource views**

Add before PrefixList views:

```python
#
# IRRSource views
#


@register_model_view(IRRSource)
class IRRSourceView(generic.ObjectView):
    queryset = IRRSource.objects.all()

    def get_extra_context(self, request, instance):
        prefix_lists = instance.prefix_lists.all()
        prefix_lists_table = PrefixListTable(prefix_lists)
        prefix_lists_table.configure(request)
        return {
            "prefix_lists_table": prefix_lists_table,
        }


@register_model_view(IRRSource, "list", path="")
class IRRSourceListView(generic.ObjectListView):
    queryset = IRRSource.objects.annotate(
        prefix_list_count=Count("prefix_lists")
    )
    table = IRRSourceTable
    filterset = IRRSourceFilterSet
    filterset_form = IRRSourceFilterForm


@register_model_view(IRRSource, "add")
@register_model_view(IRRSource, "edit")
class IRRSourceEditView(generic.ObjectEditView):
    queryset = IRRSource.objects.all()
    form = IRRSourceForm


@register_model_view(IRRSource, "delete")
class IRRSourceDeleteView(generic.ObjectDeleteView):
    queryset = IRRSource.objects.all()


@register_model_view(IRRSource, "bulk_edit", path="edit")
class IRRSourceBulkEditView(generic.BulkEditView):
    queryset = IRRSource.objects.all()
    table = IRRSourceTable
    form = IRRSourceBulkEditForm
    filterset = IRRSourceFilterSet


@register_model_view(IRRSource, "bulk_delete", path="delete")
class IRRSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = IRRSource.objects.all()
    table = IRRSourceTable
    filterset = IRRSourceFilterSet


@register_model_view(IRRSource, "bulk_import", path="import")
class IRRSourceBulkImportView(generic.BulkImportView):
    queryset = IRRSource.objects.all()
    model_form = IRRSourceImportForm
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/views.py
git commit -m "feat: add IRRSource views"
```

---

## Task 7: Add IRRSource Template

**Files:**
- Create: `netbox_peering_manager/templates/netbox_peering_manager/irrsource.html`

**Step 1: Create template**

```html
{% extends 'generic/object.html' %}
{% load render_table from django_tables2 %}
{% load helpers %}
{% load plugins %}

{% block content %}
<div class="row mb-3">
    <div class="col col-md-6">
        <div class="card">
            <h5 class="card-header">IRR Source</h5>
            <table class="table table-hover attr-table">
                <tr>
                    <th scope="row">Name</th>
                    <td>{{ object.name }}</td>
                </tr>
                <tr>
                    <th scope="row">URL</th>
                    <td><a href="{{ object.url }}">{{ object.url }}</a></td>
                </tr>
                <tr>
                    <th scope="row">IRR Sources</th>
                    <td>{{ object.sources|default:"&mdash;" }}</td>
                </tr>
                <tr>
                    <th scope="row">Cache TTL</th>
                    <td>{{ object.cache_ttl|default:"Default" }} seconds</td>
                </tr>
                <tr>
                    <th scope="row">Sync Interval</th>
                    <td>{{ object.sync_interval }} minutes</td>
                </tr>
                <tr>
                    <th scope="row">Enabled</th>
                    <td>{% checkmark object.enabled %}</td>
                </tr>
                <tr>
                    <th scope="row">Description</th>
                    <td>{{ object.description|default:"&mdash;" }}</td>
                </tr>
            </table>
        </div>
        {% include 'inc/panels/tags.html' %}
        {% include 'inc/panels/comments.html' %}
        {% plugin_left_page object %}
    </div>
    <div class="col col-md-6">
        {% include 'inc/panels/custom_fields.html' %}
        {% plugin_right_page object %}
    </div>
</div>
<div class="row">
    <div class="col col-md-12">
        <div class="card">
            <h5 class="card-header">Prefix Lists</h5>
            <div class="card-body table-responsive">
                {% render_table prefix_lists_table %}
            </div>
        </div>
        {% plugin_full_width_page object %}
    </div>
</div>
{% endblock %}
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/templates/netbox_peering_manager/irrsource.html
git commit -m "feat: add IRRSource template"
```

---

## Task 8: Update Navigation Menu

**Files:**
- Modify: `netbox_peering_manager/navigation.py`

**Step 1: Add IRRSource menu item**

Add to `_policies_menu` tuple (or create new section):

```python
PluginMenuItem(
    link="plugins:netbox_peering_manager:irrsource_list",
    link_text="IRR Sources",
    permissions=["netbox_peering_manager.view_irrsource"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_peering_manager:irrsource_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_peering_manager.add_irrsource"],
        ),
    ),
),
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/navigation.py
git commit -m "feat: add IRRSource to navigation menu"
```

---

## Task 9: Add IRRSource API Serializer and ViewSet

**Files:**
- Modify: `netbox_peering_manager/api/serializers.py`
- Modify: `netbox_peering_manager/api/views.py`
- Modify: `netbox_peering_manager/api/urls.py`

**Step 1: Add IRRSourceSerializer**

In `serializers.py`, add import and serializer:

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)

class IRRSourceSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:irrsource-detail")

    class Meta:
        model = IRRSource
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "url",
            "sources",
            "cache_ttl",
            "sync_interval",
            "enabled",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "enabled")
```

**Step 2: Update PrefixListSerializer**

Add new fields:

```python
class PrefixListSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_peering_manager-api:prefixlist-detail")
    irr_source = IRRSourceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = PrefixList
        fields = (
            "id",
            "url",
            "name",
            "display",
            "description",
            "family",
            "source_as_set",
            "irr_source",
            "tags",
            "custom_fields",
            "comments",
        )
        brief_fields = ("id", "url", "display", "name", "description")
```

**Step 3: Add IRRSourceViewSet in views.py**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
from netbox_peering_manager.api.serializers import (
    # ... existing imports ...
    IRRSourceSerializer,
)
from netbox_peering_manager.filtersets import (
    # ... existing imports ...
    IRRSourceFilterSet,
)

class IRRSourceViewSet(NetBoxModelViewSet):
    queryset = IRRSource.objects.all()
    serializer_class = IRRSourceSerializer
    filterset_class = IRRSourceFilterSet
```

**Step 4: Register URL in urls.py**

```python
router.register("irr-source", IRRSourceViewSet)
```

**Step 5: Commit**

```bash
git add netbox_peering_manager/api/serializers.py netbox_peering_manager/api/views.py netbox_peering_manager/api/urls.py
git commit -m "feat: add IRRSource API serializer, viewset, and URL"
```

---

## Task 10: Add IRRSource GraphQL Types

**Files:**
- Modify: `netbox_peering_manager/graphql/types.py`
- Modify: `netbox_peering_manager/graphql/filters.py`
- Modify: `netbox_peering_manager/graphql/schema.py`

**Step 1: Add filter in filters.py**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)

@strawberry_django.filter_type(IRRSource, lookups=True)
class NetBoxBGPIRRSourceFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
```

Update `__all__` to include `"NetBoxBGPIRRSourceFilter"`.

**Step 2: Add type in types.py**

```python
from netbox_peering_manager.models import (
    # ... existing imports ...
    IRRSource,
)
from .filters import (
    # ... existing imports ...
    NetBoxBGPIRRSourceFilter,
)

@strawberry_django.type(IRRSource, fields="__all__", filters=NetBoxBGPIRRSourceFilter)
class IRRSourceType(NetBoxObjectType):
    name: str
    slug: str
    url: str
    sources: str
    cache_ttl: int | None
    sync_interval: int
    enabled: bool
    description: str
    prefix_lists: list[Annotated["PrefixListType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
```

Update `PrefixListType` to include new fields:

```python
@strawberry_django.type(PrefixList, fields="__all__", filters=NetBoxBGPPrefixListFilter)
class PrefixListType(NetBoxObjectType):
    name: str
    description: str
    family: str
    source_as_set: str
    irr_source: Annotated["IRRSourceType", strawberry.lazy("netbox_peering_manager.graphql.types")] | None
    prefrules: list[Annotated["PrefixListRuleType", strawberry.lazy("netbox_peering_manager.graphql.types")]]
```

**Step 3: Add to schema.py**

```python
from .types import (
    # ... existing imports ...
    IRRSourceType,
)

# In NetBoxBGPQuery class:
    netbox_peering_manager_irr_source: IRRSourceType = strawberry_django.field()
    netbox_peering_manager_irr_source_list: list[IRRSourceType] = strawberry_django.field()
```

**Step 4: Commit**

```bash
git add netbox_peering_manager/graphql/types.py netbox_peering_manager/graphql/filters.py netbox_peering_manager/graphql/schema.py
git commit -m "feat: add IRRSource GraphQL types and schema"
```

---

## Task 11: Create IRR Client Module

**Files:**
- Create: `netbox_peering_manager/irr_client.py`

**Step 1: Create IRR client**

```python
"""
Client for communicating with fastbgpq4 API.
"""

import logging
import time
from typing import Any

import httpx

from netbox_peering_manager.models import IRRSource

logger = logging.getLogger(__name__)

# Configuration defaults
DEFAULT_TIMEOUT = 30.0
POLL_INTERVAL = 2.0
MAX_POLL_ATTEMPTS = 150  # 5 minutes max with 2s interval


class IRRClientError(Exception):
    """Base exception for IRR client errors."""

    pass


class IRRClient:
    """Client for querying fastbgpq4 API."""

    def __init__(self, irr_source: IRRSource):
        self.irr_source = irr_source
        self.base_url = irr_source.url.rstrip("/")

    def _build_params(self, as_set: str, family: str) -> dict[str, Any]:
        """Build query parameters for fastbgpq4 API."""
        params = {
            "target": as_set,
            "format": "json",
        }
        if self.irr_source.sources:
            params["sources"] = self.irr_source.sources
        if self.irr_source.cache_ttl:
            params["cache_ttl"] = self.irr_source.cache_ttl

        # Filter by address family
        if family == "ipv4":
            params["max_masklen"] = 32
        elif family == "ipv6":
            params["min_masklen"] = 33  # Only IPv6 prefixes

        return params

    def fetch_prefixes(self, as_set: str, family: str = "both") -> list[str]:
        """
        Fetch prefixes for an AS-SET from fastbgpq4.

        Args:
            as_set: The AS-SET to query (e.g., AS-HURRICANE)
            family: Address family filter (ipv4, ipv6, or both)

        Returns:
            List of prefix strings (e.g., ["192.0.2.0/24", "2001:db8::/32"])
        """
        prefixes = []

        if family in ("ipv4", "both"):
            prefixes.extend(self._fetch_family(as_set, "ipv4"))

        if family in ("ipv6", "both"):
            prefixes.extend(self._fetch_family(as_set, "ipv6"))

        return prefixes

    def _fetch_family(self, as_set: str, family: str) -> list[str]:
        """Fetch prefixes for a specific address family."""
        params = self._build_params(as_set, family)
        url = f"{self.base_url}/api/v1/as-set/expand"

        logger.info(f"Fetching {family} prefixes for {as_set} from {url}")

        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(url, params=params)

            if response.status_code == 202:
                # Async mode - poll for results
                job_data = response.json()
                return self._poll_job(client, job_data["job_id"])

            response.raise_for_status()
            data = response.json()

            # fastbgpq4 returns {"data": {"nn": ["prefix1", "prefix2", ...]}}
            if "data" in data and "nn" in data["data"]:
                return data["data"]["nn"]
            elif "data" in data:
                # Handle alternative response format
                return list(data["data"].values())[0] if data["data"] else []

            return []

    def _poll_job(self, client: httpx.Client, job_id: str) -> list[str]:
        """Poll for async job completion."""
        poll_url = f"{self.base_url}/api/v1/jobs/{job_id}"

        for attempt in range(MAX_POLL_ATTEMPTS):
            time.sleep(POLL_INTERVAL)
            response = client.get(poll_url)
            response.raise_for_status()

            job_data = response.json()
            status = job_data.get("status")

            if status == "completed":
                data = job_data.get("data", {})
                if "nn" in data:
                    return data["nn"]
                return list(data.values())[0] if data else []

            if status == "failed":
                error = job_data.get("error", "Unknown error")
                raise IRRClientError(f"Job failed: {error}")

            logger.debug(f"Job {job_id} still processing (attempt {attempt + 1})")

        raise IRRClientError(f"Job {job_id} timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/irr_client.py
git commit -m "feat: add IRR client for fastbgpq4 API"
```

---

## Task 12: Create Sync Jobs

**Files:**
- Create: `netbox_peering_manager/jobs.py`

**Step 1: Create jobs module**

```python
"""
Background jobs for IRR prefix list synchronization.
"""

import logging

from core.choices import JobStatusChoices
from netbox.jobs import JobRunner

from netbox_peering_manager.irr_client import IRRClient, IRRClientError
from netbox_peering_manager.models import IRRSource, PrefixList, PrefixListRule

logger = logging.getLogger(__name__)


class SyncPrefixListJob(JobRunner):
    """Sync a single PrefixList from IRR."""

    class Meta:
        name = "Sync Prefix List from IRR"

    def run(self, *args, **kwargs):
        prefix_list = self.job.object

        if not prefix_list.is_irr_managed:
            self.job.data = {"error": "PrefixList is not IRR-managed"}
            self.job.status = JobStatusChoices.STATUS_ERRORED
            return

        irr_source = prefix_list.irr_source
        as_set = prefix_list.source_as_set
        family = prefix_list.family

        self.job.data = {
            "as_set": as_set,
            "irr_source": irr_source.name,
            "family": family,
        }

        try:
            client = IRRClient(irr_source)
            prefixes = client.fetch_prefixes(as_set, family)

            # Delete existing rules
            deleted_count = prefix_list.prefrules.count()
            prefix_list.prefrules.all().delete()

            # Create new rules
            rules = []
            for index, prefix in enumerate(prefixes):
                rules.append(
                    PrefixListRule(
                        prefix_list=prefix_list,
                        index=(index + 1) * 10,
                        action="permit",
                        prefix_custom=prefix,
                    )
                )

            PrefixListRule.objects.bulk_create(rules)

            self.job.data.update({
                "deleted_rules": deleted_count,
                "created_rules": len(rules),
                "prefixes": len(prefixes),
            })

            logger.info(
                f"Synced {len(prefixes)} prefixes for {prefix_list.name} "
                f"from {as_set} ({deleted_count} deleted, {len(rules)} created)"
            )

        except IRRClientError as e:
            self.job.data["error"] = str(e)
            self.job.status = JobStatusChoices.STATUS_ERRORED
            logger.error(f"IRR sync failed for {prefix_list.name}: {e}")
            raise

        except Exception as e:
            self.job.data["error"] = str(e)
            self.job.status = JobStatusChoices.STATUS_ERRORED
            logger.exception(f"Unexpected error syncing {prefix_list.name}")
            raise


class SyncAllPrefixListsJob(JobRunner):
    """Sync all IRR-managed PrefixLists for an IRRSource."""

    class Meta:
        name = "Sync All Prefix Lists from IRR"

    def run(self, *args, **kwargs):
        irr_source = self.job.object

        if not irr_source.enabled:
            self.job.data = {"error": "IRR source is disabled"}
            self.job.status = JobStatusChoices.STATUS_ERRORED
            return

        prefix_lists = PrefixList.objects.filter(
            irr_source=irr_source,
            source_as_set__isnull=False,
        ).exclude(source_as_set="")

        self.job.data = {
            "irr_source": irr_source.name,
            "total_prefix_lists": prefix_lists.count(),
            "synced": 0,
            "failed": 0,
            "errors": [],
        }

        client = IRRClient(irr_source)

        for prefix_list in prefix_lists:
            try:
                prefixes = client.fetch_prefixes(
                    prefix_list.source_as_set,
                    prefix_list.family,
                )

                prefix_list.prefrules.all().delete()

                rules = []
                for index, prefix in enumerate(prefixes):
                    rules.append(
                        PrefixListRule(
                            prefix_list=prefix_list,
                            index=(index + 1) * 10,
                            action="permit",
                            prefix_custom=prefix,
                        )
                    )

                PrefixListRule.objects.bulk_create(rules)
                self.job.data["synced"] += 1

                logger.info(f"Synced {len(prefixes)} prefixes for {prefix_list.name}")

            except Exception as e:
                self.job.data["failed"] += 1
                self.job.data["errors"].append({
                    "prefix_list": prefix_list.name,
                    "error": str(e),
                })
                logger.error(f"Failed to sync {prefix_list.name}: {e}")

        if self.job.data["failed"] > 0:
            self.job.status = JobStatusChoices.STATUS_ERRORED
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/jobs.py
git commit -m "feat: add IRR sync jobs"
```

---

## Task 13: Add Sync Action to PrefixList View

**Files:**
- Modify: `netbox_peering_manager/views.py`
- Modify: `netbox_peering_manager/templates/netbox_peering_manager/prefixlist.html`

**Step 1: Add sync view**

Add after PrefixListView:

```python
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from utilities.permissions import get_permission_for_model

from netbox_peering_manager.jobs import SyncPrefixListJob


class PrefixListSyncView(View):
    """Trigger IRR sync for a PrefixList."""

    def post(self, request, pk):
        prefix_list = get_object_or_404(PrefixList, pk=pk)

        if not prefix_list.is_irr_managed:
            messages.error(request, "This prefix list is not IRR-managed.")
            return redirect(prefix_list.get_absolute_url())

        # Enqueue sync job
        SyncPrefixListJob.enqueue(instance=prefix_list, user=request.user)
        messages.success(request, f"Sync job enqueued for {prefix_list.name}")

        return redirect(prefix_list.get_absolute_url())
```

**Step 2: Add URL pattern**

In the URL patterns (you may need to create/modify `urls.py`), add:

```python
path(
    "prefix-list/<int:pk>/sync/",
    PrefixListSyncView.as_view(),
    name="prefixlist_sync",
),
```

**Step 3: Update PrefixList template**

Add sync button to the template header buttons (in `prefixlist.html`):

```html
{% if object.is_irr_managed %}
<form method="post" action="{% url 'plugins:netbox_peering_manager:prefixlist_sync' pk=object.pk %}" class="d-inline">
    {% csrf_token %}
    <button type="submit" class="btn btn-primary">
        <i class="mdi mdi-sync"></i> Sync from IRR
    </button>
</form>
{% endif %}
```

Add IRR status to the detail panel:

```html
<tr>
    <th scope="row">IRR Managed</th>
    <td>
        {% if object.is_irr_managed %}
            <span class="badge bg-success">Yes</span>
            ({{ object.source_as_set }} via {{ object.irr_source }})
        {% else %}
            <span class="badge bg-secondary">No</span>
        {% endif %}
    </td>
</tr>
```

**Step 4: Commit**

```bash
git add netbox_peering_manager/views.py netbox_peering_manager/templates/netbox_peering_manager/prefixlist.html
git commit -m "feat: add sync action to PrefixList view"
```

---

## Task 14: Register Jobs in Plugin Config

**Files:**
- Modify: `netbox_peering_manager/__init__.py`

**Step 1: Update plugin config**

Add jobs to the plugin configuration:

```python
class NetBoxPeeringManagerConfig(PluginConfig):
    # ... existing config ...

    def ready(self):
        super().ready()
        # Import jobs to register them
        from netbox_peering_manager import jobs  # noqa: F401
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/__init__.py
git commit -m "feat: register IRR sync jobs in plugin config"
```

---

## Task 15: Add httpx Dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add httpx to dependencies**

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "httpx>=0.27.0",
]
```

**Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add httpx dependency for IRR client"
```

---

## Task 16: Update PrefixList Detail Template

**Files:**
- Modify: `netbox_peering_manager/templates/netbox_peering_manager/prefixlist.html`

**Step 1: Read and update template**

Ensure the template shows IRR information and sync button. The template should include:

1. IRR status badge in the detail panel
2. Sync button in the header (only for IRR-managed lists)
3. Source AS-SET and IRR Source fields
4. Link to related job history

**Step 2: Commit**

```bash
git add netbox_peering_manager/templates/netbox_peering_manager/prefixlist.html
git commit -m "feat: update PrefixList template with IRR status and sync button"
```

---

## Task 17: Run Linting and Fix Issues

**Step 1: Run ruff**

```bash
uvx ruff check --fix netbox_peering_manager/
```

**Step 2: Commit fixes**

```bash
git add -A
git commit -m "chore: fix linting issues"
```

---

## Task 18: Verify Syntax

**Step 1: Check Python syntax**

```bash
python3 -m py_compile netbox_peering_manager/models.py netbox_peering_manager/jobs.py netbox_peering_manager/irr_client.py
```

**Step 2: If errors, fix and commit**

---

## Task 19: Final Review and Push

**Step 1: Review all changes**

```bash
git log --oneline -20
git diff origin/develop..HEAD --stat
```

**Step 2: Push to origin**

```bash
git push origin develop
```

---

## Summary

This plan implements:

1. **IRRSource model** - Configuration for fastbgpq4 instances
2. **PrefixList extensions** - `source_as_set` and `irr_source` fields
3. **IRR client** - httpx-based client for fastbgpq4 API
4. **Sync jobs** - NetBox JobRunner-based background sync
5. **UI** - Views, forms, tables, templates for IRRSource
6. **API/GraphQL** - Full CRUD support for IRRSource
7. **Sync action** - Manual trigger button on PrefixList detail

Sources:
- [NetBox Background Jobs Documentation](https://netboxlabs.com/docs/netbox/plugins/development/background-jobs/)
- [NetBox Jobs Model](https://netboxlabs.com/docs/netbox/en/stable/models/core/job/)
