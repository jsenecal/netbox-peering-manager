"""Jinja2 filters for BGP configuration templating.

This module provides custom Jinja2 filters for generating vendor-specific
BGP configuration syntax from NetBox peering manager data.
"""

import ipaddress
from collections import defaultdict
from collections.abc import Generator
from typing import Any


def as_path_regex(asn: int, vendor: str = "cisco") -> str:
    """Convert an ASN to AS-path regex format.

    Args:
        asn: The AS number to convert.
        vendor: Target vendor format ('cisco' or 'junos'). Defaults to 'cisco'.

    Returns:
        AS-path regex string in vendor-specific format.
        - Cisco: ^{asn}_
        - Junos: ^{asn} (with trailing space)
    """
    if vendor == "junos":
        return f"^{asn} "
    # Default to Cisco format for unknown vendors
    return f"^{asn}_"


def ip_network(prefix: str) -> dict:
    """Parse a prefix into a dictionary with network details.

    Args:
        prefix: IP prefix in CIDR notation (e.g., '192.168.1.0/24').

    Returns:
        Dictionary containing:
        - network: Network address as string
        - prefix_length: Integer prefix length
        - netmask: Netmask as string
    """
    net = ipaddress.ip_network(prefix, strict=False)
    return {
        "network": str(net.network_address),
        "prefix_length": net.prefixlen,
        "netmask": str(net.netmask),
    }


def group_by(items: list, attr: str) -> Generator[tuple[Any, list], None, None]:
    """Group objects by attribute value.

    Args:
        items: List of objects or dictionaries to group.
        attr: Attribute name or dictionary key to group by.

    Yields:
        Tuples of (key, list of items with that key value).
    """
    groups = defaultdict(list)
    for item in items:
        if isinstance(item, dict):
            key = item.get(attr)
        else:
            key = getattr(item, attr, None)
        groups[key].append(item)

    for key, group_items in groups.items():
        yield (key, group_items)


def to_community_list(value: str, name: str, vendor: str = "cisco") -> str:
    """Convert a community value to vendor-specific community list syntax.

    Args:
        value: Community value (e.g., '65000:100' or '4200000001:100:200').
        name: Name for the community list.
        vendor: Target vendor format ('cisco' or 'junos'). Defaults to 'cisco'.

    Returns:
        Vendor-specific community list configuration string.
    """
    if vendor == "junos":
        return f"""policy-options {{
    community {name} members {value};
}}"""
    # Default to Cisco format
    return f"ip community-list standard {name} permit {value}"


def to_prefix_set(prefixes: list, name: str, vendor: str = "cisco") -> str:
    """Convert a list of prefixes to vendor-specific prefix list syntax.

    Args:
        prefixes: List of dicts with 'prefix' key, optionally 'ge' and 'le'.
        name: Name for the prefix list.
        vendor: Target vendor format ('cisco' or 'junos'). Defaults to 'cisco'.

    Returns:
        Vendor-specific prefix list configuration string.
    """
    if not prefixes:
        return ""

    lines = []

    if vendor == "junos":
        lines.append("policy-options {")
        lines.append(f"    prefix-list {name} {{")
        for entry in prefixes:
            prefix = entry.get("prefix", "")
            ge = entry.get("ge")
            le = entry.get("le")
            if ge is not None and le is not None:
                # Junos uses prefix-length-range notation
                lines.append(f"        {prefix} prefix-length-range /{ge}-/{le};")
            elif ge is not None:
                lines.append(f"        {prefix} prefix-length-range /{ge}-/32;")
            elif le is not None:
                lines.append(f"        {prefix} upto /{le};")
            else:
                lines.append(f"        {prefix};")
        lines.append("    }")
        lines.append("}")
    else:
        # Default to Cisco format
        seq = 10
        for entry in prefixes:
            prefix = entry.get("prefix", "")
            ge = entry.get("ge")
            le = entry.get("le")

            line = f"ip prefix-list {name} seq {seq} permit {prefix}"
            if ge is not None:
                line += f" ge {ge}"
            if le is not None:
                line += f" le {le}"
            lines.append(line)
            seq += 10

    return "\n".join(lines)


# Export dictionary mapping filter names to functions
PEERING_FILTERS = {
    "as_path_regex": as_path_regex,
    "ip_network": ip_network,
    "group_by": group_by,
    "to_community_list": to_community_list,
    "to_prefix_set": to_prefix_set,
}
