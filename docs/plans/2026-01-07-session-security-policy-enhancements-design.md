# Phase 4: Session Security & Policy Enhancements Design

**Date:** 2026-01-07
**Phase:** 4
**Status:** Approved

## Overview

Add BGP session password support and routing policy enhancements. Also migrate to NetBox core's IPAddressFamilyChoices for consistency.

## Scope

### What we're building:
- `BGPSession.password` - plain CharField for MD5 authentication password
- `RoutingPolicy.weight` - PositiveIntegerField for evaluation ordering
- `RoutingPolicy.address_family` - CharField with NetBox core IPAddressFamilyChoices or null
- Enhanced Community validation - named regex groups with strict 2-byte AS range checks
- Migration from plugin's string-based IPAddressFamilyChoices to NetBox core's integer-based version

### What we're skipping (YAGNI):
- `RoutingPolicy.type` (ingress/egress) - already handled by M2M field names (import_policies/export_policies)
- `Community.type` - usage context determines application

## Model Changes

### BGPSession

```python
class BGPSession(NetBoxModel):
    # ... existing fields ...

    # Phase 4: Session security
    password = models.CharField(
        max_length=256,
        blank=True,
        help_text="MD5 authentication password for this session"
    )
```

### RoutingPolicy

```python
from ipam.choices import IPAddressFamilyChoices

class RoutingPolicy(NetBoxModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)

    # Phase 4: Policy enhancements
    weight = models.PositiveIntegerField(
        default=0,
        help_text="Higher weight policies are evaluated first"
    )
    address_family = models.PositiveSmallIntegerField(
        choices=IPAddressFamilyChoices,
        blank=True,
        null=True,
        help_text="Restrict policy to specific address family"
    )

    class Meta:
        verbose_name_plural = "Routing Policies"
        ordering = ["-weight", "name"]
```

### PrefixList (Migration)

```python
from ipam.choices import IPAddressFamilyChoices

class PrefixList(NetBoxModel):
    # Change from CharField to PositiveSmallIntegerField
    family = models.PositiveSmallIntegerField(
        choices=IPAddressFamilyChoices,
        help_text="Address family (IPv4 or IPv6)"
    )
```

**Data Migration:** Convert existing string values to integers:
- `"ipv4"` → `4`
- `"ipv6"` → `6`

## Community Validator

New file: `validators.py`

```python
import re
from django.core.exceptions import ValidationError

REGEX_STANDARD = re.compile(r"^(?P<asn>\d+):(?P<value>\d+)$")
REGEX_LARGE = re.compile(r"^(?P<global_admin>\d+):(?P<local_data1>\d+):(?P<local_data2>\d+)$")
REGEX_EXTENDED = re.compile(
    r"^(?P<type>RT|SoO|0x[a-fA-F0-9]{2}):(?P<admin>\d+|0x[a-fA-F0-9]+):(?P<value>\d+|0x[a-fA-F0-9]+)$"
)

def validate_community(value):
    """Validate BGP community value format and ranges."""

    # Standard community: <0-65535>:<0-65535>
    if match := REGEX_STANDARD.match(value):
        asn = int(match.group("asn"))
        val = int(match.group("value"))
        if not (0 <= asn <= 65535 and 0 <= val <= 65535):
            raise ValidationError(
                "Standard community must be <0-65535>:<0-65535>"
            )
        return

    # Large community: <4-byte>:<4-byte>:<4-byte>
    if match := REGEX_LARGE.match(value):
        for field in ("global_admin", "local_data1", "local_data2"):
            if int(match.group(field)) > 4294967295:
                raise ValidationError(
                    "Large community values must be <0-4294967295>"
                )
        return

    # Extended community: (RT|SoO|0xNN):<admin>:<value>
    if REGEX_EXTENDED.match(value):
        return  # Format valid, hex/decimal values accepted

    raise ValidationError(
        "Invalid community format. Use standard (ASN:VAL), "
        "large (GA:LD1:LD2), or extended (RT|SoO:ADMIN:VAL)"
    )
```

### Community Model Update

```python
from netbox_peering_manager.validators import validate_community

class Community(BGPBase):
    value = models.CharField(
        max_length=64,
        validators=[validate_community]
    )
```

## Files Affected

| File | Changes |
|------|---------|
| `models.py` | Add password, weight, address_family fields; update Community validator; change PrefixList.family type |
| `validators.py` | New file with validate_community function |
| `choices.py` | Remove IPAddressFamilyChoices (use NetBox core) |
| `forms.py` | Update forms for new fields; migrate to core IPAddressFamilyChoices |
| `tables.py` | Add columns for new fields |
| `filtersets.py` | Add filters for new fields |
| `api/serializers.py` | Add new fields to serializers |
| `graphql/types.py` | Add new fields to GraphQL types |
| `graphql/enums.py` | Remove IPAddressFamilyChoices enum (use core) |
| `tests/` | Update tests for new fields and validator |
| `migrations/` | Schema changes + data migration for family field |

## Migration Strategy

The `PrefixList.family` migration requires careful handling:

1. Add new integer field `family_new` with null=True
2. Data migration: copy values (`"ipv4"` → 4, `"ipv6"` → 6)
3. Remove old `family` CharField
4. Rename `family_new` to `family`
5. Set null=False

Or use a single migration with `migrations.RunPython` for data conversion.

## Testing

- Unit tests for `validate_community` with all formats and edge cases
- Model tests for new fields
- API tests for serializer changes
- Form validation tests
