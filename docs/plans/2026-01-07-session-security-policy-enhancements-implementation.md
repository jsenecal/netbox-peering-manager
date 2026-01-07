# Phase 4: Session Security & Policy Enhancements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add BGP session password, routing policy weight/address_family fields, enhanced community validation, and migrate to NetBox core IPAddressFamilyChoices.

**Architecture:** Add new fields to existing models, create a validators module for community validation, and migrate PrefixList.family from string to integer type using NetBox core choices.

**Tech Stack:** Django 5.x, NetBox 4.4+, Python 3.12

---

### Task 1: Create Community Validator

**Files:**
- Create: `netbox_peering_manager/validators.py`
- Test: `netbox_peering_manager/tests/test_validators.py`

**Context:** Create a new validators module with the `validate_community` function that validates BGP community formats (standard, large, extended) with strict 2-byte AS range checks.

**Step 1: Create the validator file**

Create `netbox_peering_manager/validators.py`:

```python
"""Custom validators for netbox-peering-manager."""

import re

from django.core.exceptions import ValidationError

REGEX_STANDARD = re.compile(r"^(?P<asn>\d+):(?P<value>\d+)$")
REGEX_LARGE = re.compile(r"^(?P<global_admin>\d+):(?P<local_data1>\d+):(?P<local_data2>\d+)$")
REGEX_EXTENDED = re.compile(
    r"^(?P<type>RT|SoO|0x[a-fA-F0-9]{2}):(?P<admin>\d+|0x[a-fA-F0-9]+):(?P<value>\d+|0x[a-fA-F0-9]+)$"
)


def validate_community(value):
    """
    Validate BGP community value format and ranges.

    Supports three formats:
    - Standard: <0-65535>:<0-65535>
    - Large: <0-4294967295>:<0-4294967295>:<0-4294967295>
    - Extended: (RT|SoO|0xNN):<admin>:<value>
    """
    # Standard community: <0-65535>:<0-65535>
    if match := REGEX_STANDARD.match(value):
        asn = int(match.group("asn"))
        val = int(match.group("value"))
        if not (0 <= asn <= 65535 and 0 <= val <= 65535):
            raise ValidationError("Standard community must be <0-65535>:<0-65535>")
        return

    # Large community: <4-byte>:<4-byte>:<4-byte>
    if match := REGEX_LARGE.match(value):
        for field in ("global_admin", "local_data1", "local_data2"):
            if int(match.group(field)) > 4294967295:
                raise ValidationError("Large community values must be <0-4294967295>")
        return

    # Extended community: (RT|SoO|0xNN):<admin>:<value>
    if REGEX_EXTENDED.match(value):
        return  # Format valid, hex/decimal values accepted

    raise ValidationError(
        "Invalid community format. Use standard (ASN:VAL), "
        "large (GA:LD1:LD2), or extended (RT|SoO:ADMIN:VAL)"
    )
```

**Step 2: Create test file**

Create `netbox_peering_manager/tests/test_validators.py`:

```python
"""Tests for custom validators."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from netbox_peering_manager.validators import validate_community


class ValidateCommunityTestCase(TestCase):
    """Test cases for validate_community function."""

    def test_standard_community_valid(self):
        """Valid standard communities should pass."""
        validate_community("65000:100")
        validate_community("0:0")
        validate_community("65535:65535")
        validate_community("1:1")

    def test_standard_community_invalid_asn(self):
        """Standard community with ASN > 65535 should fail."""
        with self.assertRaises(ValidationError) as ctx:
            validate_community("65536:100")
        self.assertIn("0-65535", str(ctx.exception))

    def test_standard_community_invalid_value(self):
        """Standard community with value > 65535 should fail."""
        with self.assertRaises(ValidationError) as ctx:
            validate_community("65000:65536")
        self.assertIn("0-65535", str(ctx.exception))

    def test_large_community_valid(self):
        """Valid large communities should pass."""
        validate_community("4200000001:100:200")
        validate_community("0:0:0")
        validate_community("4294967295:4294967295:4294967295")

    def test_large_community_invalid(self):
        """Large community with value > 4294967295 should fail."""
        with self.assertRaises(ValidationError) as ctx:
            validate_community("4294967296:100:200")
        self.assertIn("4294967295", str(ctx.exception))

    def test_extended_community_rt_valid(self):
        """Valid RT extended communities should pass."""
        validate_community("RT:65000:100")
        validate_community("RT:0x1234:0xABCD")

    def test_extended_community_soo_valid(self):
        """Valid SoO extended communities should pass."""
        validate_community("SoO:65000:100")

    def test_extended_community_hex_type_valid(self):
        """Valid hex-type extended communities should pass."""
        validate_community("0x02:65000:100")
        validate_community("0xAB:0x1234:0x5678")

    def test_invalid_format(self):
        """Invalid formats should fail with descriptive error."""
        with self.assertRaises(ValidationError) as ctx:
            validate_community("invalid")
        self.assertIn("Invalid community format", str(ctx.exception))

    def test_invalid_format_single_value(self):
        """Single value without colon should fail."""
        with self.assertRaises(ValidationError):
            validate_community("65000")

    def test_invalid_format_four_parts(self):
        """Four-part value should fail."""
        with self.assertRaises(ValidationError):
            validate_community("1:2:3:4")
```

**Step 3: Run tests to verify they pass**

Run: `make test`
Expected: Tests pass (validator implementation is complete)

**Step 4: Commit**

```bash
git add netbox_peering_manager/validators.py netbox_peering_manager/tests/test_validators.py
git commit -m "feat: add community validator with RFC-compliant format checks"
```

---

### Task 2: Update Community Model to Use New Validator

**Files:**
- Modify: `netbox_peering_manager/models.py`

**Context:** Replace the basic regex validator on Community.value with the new validate_community function.

**Step 1: Update the import and model**

In `netbox_peering_manager/models.py`, add import at top:

```python
from netbox_peering_manager.validators import validate_community
```

Then update the Community model's value field (around line 545):

Change from:
```python
value = models.CharField(max_length=64, validators=[RegexValidator(r"[\d\.\*]+:[\d\.\*]+")])
```

To:
```python
value = models.CharField(max_length=64, validators=[validate_community])
```

Also remove the `RegexValidator` import if no longer used elsewhere.

**Step 2: Run tests**

Run: `make test`
Expected: All tests pass

**Step 3: Commit**

```bash
git add netbox_peering_manager/models.py
git commit -m "feat: use RFC-compliant community validator"
```

---

### Task 3: Add BGPSession Password Field

**Files:**
- Modify: `netbox_peering_manager/models.py`

**Context:** Add a password field to BGPSession for MD5 authentication.

**Step 1: Add the password field**

In `netbox_peering_manager/models.py`, add to the BGPSession class after the existing Phase 1 fields (around line 760):

```python
    # Phase 4: Session security
    password = models.CharField(
        max_length=256,
        blank=True,
        help_text="MD5 authentication password for this session",
    )
```

**Step 2: Run syntax check**

Run: `python -m py_compile netbox_peering_manager/models.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add netbox_peering_manager/models.py
git commit -m "feat: add password field to BGPSession"
```

---

### Task 4: Add RoutingPolicy Weight and Address Family Fields

**Files:**
- Modify: `netbox_peering_manager/models.py`

**Context:** Add weight (for ordering) and address_family fields to RoutingPolicy. Use NetBox core's IPAddressFamilyChoices.

**Step 1: Add import for NetBox core choices**

At top of `netbox_peering_manager/models.py`, add:

```python
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
```

**Step 2: Update RoutingPolicy model**

Find the RoutingPolicy class (around line 484) and update it:

```python
class RoutingPolicy(NetBoxModel):
    """Routing policy model."""

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
        ordering = ["-weight", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_peering_manager:routingpolicy", args=[self.pk])
```

**Step 3: Run syntax check**

Run: `python -m py_compile netbox_peering_manager/models.py`
Expected: No output (success)

**Step 4: Commit**

```bash
git add netbox_peering_manager/models.py
git commit -m "feat: add weight and address_family to RoutingPolicy"
```

---

### Task 5: Migrate PrefixList.family to NetBox Core Choices

**Files:**
- Modify: `netbox_peering_manager/models.py`

**Context:** Change PrefixList.family from CharField with plugin choices to PositiveSmallIntegerField with NetBox core IPAddressFamilyChoices.

**Step 1: Update PrefixList model**

Find PrefixList class (around line 606) and change the family field:

From:
```python
family = models.CharField(max_length=10, choices=IPAddressFamilyChoices)
```

To:
```python
family = models.PositiveSmallIntegerField(choices=CoreIPAddressFamilyChoices)
```

**Step 2: Run syntax check**

Run: `python -m py_compile netbox_peering_manager/models.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add netbox_peering_manager/models.py
git commit -m "feat: migrate PrefixList.family to NetBox core choices"
```

---

### Task 6: Create Migration with Data Migration

**Files:**
- Create: `netbox_peering_manager/migrations/XXXX_phase4_security_policy.py`

**Context:** Create a migration that handles the schema changes and converts existing PrefixList.family values from strings to integers.

**Step 1: Generate the migration**

Run: `cd /opt/netbox && /opt/netbox/venv/bin/python3 netbox/manage.py makemigrations netbox_peering_manager --name phase4_security_policy`

**Step 2: Edit the migration to add data migration**

The auto-generated migration needs a data migration function added. Edit the generated file to include:

```python
from django.db import migrations, models

def convert_family_to_integer(apps, schema_editor):
    """Convert string family values to integers."""
    PrefixList = apps.get_model('netbox_peering_manager', 'PrefixList')
    mapping = {'ipv4': 4, 'ipv6': 6}
    for prefix_list in PrefixList.objects.all():
        if prefix_list.family in mapping:
            prefix_list.family = mapping[prefix_list.family]
            prefix_list.save(update_fields=['family'])

def convert_family_to_string(apps, schema_editor):
    """Reverse: convert integer family values to strings."""
    PrefixList = apps.get_model('netbox_peering_manager', 'PrefixList')
    mapping = {4: 'ipv4', 6: 'ipv6'}
    for prefix_list in PrefixList.objects.all():
        if prefix_list.family in mapping:
            prefix_list.family = mapping[prefix_list.family]
            prefix_list.save(update_fields=['family'])
```

Add `migrations.RunPython(convert_family_to_integer, convert_family_to_string)` before the field type change.

**Step 3: Run migration**

Run: `cd /opt/netbox && /opt/netbox/venv/bin/python3 netbox/manage.py migrate netbox_peering_manager`

**Step 4: Commit**

```bash
git add netbox_peering_manager/migrations/
git commit -m "feat: add migration for Phase 4 fields with family data conversion"
```

---

### Task 7: Remove Plugin IPAddressFamilyChoices

**Files:**
- Modify: `netbox_peering_manager/choices.py`

**Context:** Remove the plugin's IPAddressFamilyChoices class since we're now using NetBox core's version.

**Step 1: Remove the class from choices.py**

Remove the entire `IPAddressFamilyChoices` class from `netbox_peering_manager/choices.py`:

```python
# DELETE THIS:
class IPAddressFamilyChoices(ChoiceSet):
    FAMILY_4 = "ipv4"
    FAMILY_6 = "ipv6"

    CHOICES = (
        (FAMILY_4, "IPv4"),
        (FAMILY_6, "IPv6"),
    )
```

**Step 2: Commit**

```bash
git add netbox_peering_manager/choices.py
git commit -m "refactor: remove plugin IPAddressFamilyChoices (use NetBox core)"
```

---

### Task 8: Update Forms

**Files:**
- Modify: `netbox_peering_manager/forms.py`

**Context:** Update forms to use NetBox core IPAddressFamilyChoices and add fields for new model attributes.

**Step 1: Update imports**

Replace:
```python
from .choices import (
    CommunityStatusChoices,
    IPAddressFamilyChoices,
    PeeringStatusChoices,
    SessionStatusChoices,
)
```

With:
```python
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
from .choices import (
    CommunityStatusChoices,
    PeeringStatusChoices,
    SessionStatusChoices,
)
```

**Step 2: Update all IPAddressFamilyChoices references to CoreIPAddressFamilyChoices**

Find and replace all occurrences in forms.py.

**Step 3: Add password field to BGPSessionForm**

Find the BGPSessionForm class and add `password` to the fields.

**Step 4: Add weight and address_family to RoutingPolicyForm**

Find the RoutingPolicyForm class and add the new fields.

**Step 5: Run syntax check**

Run: `python -m py_compile netbox_peering_manager/forms.py`

**Step 6: Commit**

```bash
git add netbox_peering_manager/forms.py
git commit -m "feat: update forms for Phase 4 fields and core IPAddressFamilyChoices"
```

---

### Task 9: Update Tables

**Files:**
- Modify: `netbox_peering_manager/tables.py`

**Context:** Add columns for new fields in relevant tables.

**Step 1: Add password column to BGPSessionTable**

Add (as a boolean indicator, not showing actual password):
```python
password = tables.BooleanColumn(
    accessor="password",
    verbose_name="Password Set",
)
```

**Step 2: Add weight and address_family columns to RoutingPolicyTable**

```python
weight = tables.Column()
address_family = tables.Column()
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/tables.py
git commit -m "feat: add table columns for Phase 4 fields"
```

---

### Task 10: Update Filtersets

**Files:**
- Modify: `netbox_peering_manager/filtersets.py`

**Context:** Add filters for new fields.

**Step 1: Update imports**

Add NetBox core choices import:
```python
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
```

Update any existing IPAddressFamilyChoices references.

**Step 2: Add filter to BGPSessionFilterSet**

```python
has_password = django_filters.BooleanFilter(
    field_name="password",
    lookup_expr="isnull",
    exclude=True,
    label="Has password",
)
```

**Step 3: Add filters to RoutingPolicyFilterSet**

```python
weight = django_filters.NumberFilter()
weight__gte = django_filters.NumberFilter(field_name="weight", lookup_expr="gte")
weight__lte = django_filters.NumberFilter(field_name="weight", lookup_expr="lte")
address_family = django_filters.MultipleChoiceFilter(choices=CoreIPAddressFamilyChoices)
```

**Step 4: Commit**

```bash
git add netbox_peering_manager/filtersets.py
git commit -m "feat: add filtersets for Phase 4 fields"
```

---

### Task 11: Update API Serializers

**Files:**
- Modify: `netbox_peering_manager/api/serializers.py`

**Context:** Add new fields to serializers and update IPAddressFamilyChoices references.

**Step 1: Update imports**

Add:
```python
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
```

**Step 2: Add password to BGPSessionSerializer**

Add `password` to the fields list. Consider making it write-only:
```python
password = serializers.CharField(write_only=True, required=False, allow_blank=True)
```

**Step 3: Add weight and address_family to RoutingPolicySerializer**

Add both fields to the serializer's Meta.fields.

**Step 4: Update PrefixListSerializer**

Update any family field handling for integer values.

**Step 5: Commit**

```bash
git add netbox_peering_manager/api/serializers.py
git commit -m "feat: update API serializers for Phase 4 fields"
```

---

### Task 12: Update GraphQL Types and Enums

**Files:**
- Modify: `netbox_peering_manager/graphql/types.py`
- Modify: `netbox_peering_manager/graphql/enums.py`

**Context:** Add new fields to GraphQL types and remove plugin IPAddressFamilyChoices enum.

**Step 1: Update enums.py**

Remove the IPAddressFamilyChoices import and enum definition. Use NetBox core's if needed.

**Step 2: Update types.py**

Add to BGPSessionType:
```python
password: str  # Note: Consider if this should be exposed in GraphQL
```

Add to RoutingPolicyType:
```python
weight: int
address_family: int | None
```

**Step 3: Commit**

```bash
git add netbox_peering_manager/graphql/types.py netbox_peering_manager/graphql/enums.py
git commit -m "feat: update GraphQL for Phase 4 fields"
```

---

### Task 13: Update Tests

**Files:**
- Modify: `netbox_peering_manager/tests/test_api.py`

**Context:** Update tests to use NetBox core IPAddressFamilyChoices and add tests for new fields.

**Step 1: Update imports**

Replace:
```python
from netbox_peering_manager.choices import (
    ActionChoices,
    IPAddressFamilyChoices,
    SessionStatusChoices,
)
```

With:
```python
from ipam.choices import IPAddressFamilyChoices as CoreIPAddressFamilyChoices
from netbox_peering_manager.choices import (
    ActionChoices,
    SessionStatusChoices,
)
```

**Step 2: Update all test references**

Change `IPAddressFamilyChoices.FAMILY_4` to `CoreIPAddressFamilyChoices.FAMILY_4` (which is `4`).
Change `IPAddressFamilyChoices.FAMILY_6` to `CoreIPAddressFamilyChoices.FAMILY_6` (which is `6`).

**Step 3: Add tests for new fields**

Add test data for BGPSession with password, RoutingPolicy with weight/address_family.

**Step 4: Run tests**

Run: `make test`
Expected: All tests pass

**Step 5: Commit**

```bash
git add netbox_peering_manager/tests/
git commit -m "test: update tests for Phase 4 fields and core IPAddressFamilyChoices"
```

---

### Task 14: Update Documentation

**Files:**
- Modify: `docs/FEATURE_GAP_ANALYSIS.md`

**Context:** Mark Phase 4 as complete.

**Step 1: Update the gap analysis document**

Update the Phase 4 section to show completion status and update the feature matrix.

**Step 2: Commit**

```bash
git add docs/FEATURE_GAP_ANALYSIS.md
git commit -m "docs: mark Phase 4 as complete"
```

---

### Task 15: Final Verification

**Context:** Run all tests and verify the implementation is complete.

**Step 1: Run linting**

Run: `ruff check netbox_peering_manager/`
Expected: All checks passed

**Step 2: Run full test suite**

Run: `make test`
Expected: All tests pass

**Step 3: Verify git status**

Run: `git status`
Expected: Clean working directory

**Step 4: Push changes**

Run: `git push origin develop`
