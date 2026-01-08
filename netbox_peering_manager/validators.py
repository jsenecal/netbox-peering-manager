"""Custom validators for netbox-peering-manager."""

import re

from django.core.exceptions import ValidationError

REGEX_STANDARD = re.compile(r"^(?P<asn>\d+):(?P<value>\d+)$")
REGEX_LARGE = re.compile(r"^(?P<global_admin>\d+):(?P<local_data1>\d+):(?P<local_data2>\d+)$")
REGEX_EXTENDED = re.compile(
    r"^(?P<type>RT|SoO|0x[a-fA-F0-9]{2}):(?P<admin>\d+|0x[a-fA-F0-9]+):(?P<value>\d+|0x[a-fA-F0-9]+)$"
)

# Error messages
MSG_STANDARD_COMMUNITY = "Standard community must be <0-65535>:<0-65535>"
MSG_LARGE_COMMUNITY = "Large community values must be <0-4294967295>"
MSG_INVALID_FORMAT = (
    "Invalid community format. Use standard (ASN:VAL), large (GA:LD1:LD2), or extended (RT|SoO:ADMIN:VAL)"
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
            raise ValidationError(MSG_STANDARD_COMMUNITY)
        return

    # Large community: <4-byte>:<4-byte>:<4-byte>
    if match := REGEX_LARGE.match(value):
        for field in ("global_admin", "local_data1", "local_data2"):
            if int(match.group(field)) > 4294967295:
                raise ValidationError(MSG_LARGE_COMMUNITY)
        return

    # Extended community: (RT|SoO|0xNN):<admin>:<value>
    if REGEX_EXTENDED.match(value):
        return  # Format valid, hex/decimal values accepted

    raise ValidationError(MSG_INVALID_FORMAT)
