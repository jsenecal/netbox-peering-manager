# Configuration Templating Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add BGP configuration templating with custom Jinja2 filters and a render endpoint that builds device/session context.

**Architecture:** Create a ConfigRenderer service that gathers BGP session data, register custom Jinja2 filters via plugin ready(), add a render-config API endpoint following NetBox's ConfigTemplateRenderMixin pattern.

**Tech Stack:** NetBox ConfigTemplate, Jinja2, Django REST Framework, NetBox API mixins

---

## Task 1: Create Jinja2 Filter Module

**Files:**
- Create: `netbox_peering_manager/jinja2_filters.py`
- Test: `netbox_peering_manager/tests/test_jinja2_filters.py`

**Step 1: Write the failing test**

```python
# netbox_peering_manager/tests/test_jinja2_filters.py
from django.test import TestCase

from netbox_peering_manager.jinja2_filters import (
    as_path_regex,
    group_by,
    ip_network,
    to_community_list,
    to_prefix_set,
)


class AsPathRegexFilterTest(TestCase):
    def test_cisco_format(self):
        result = as_path_regex(65001)
        self.assertEqual(result, "^65001_")

    def test_cisco_explicit(self):
        result = as_path_regex(65001, vendor="cisco")
        self.assertEqual(result, "^65001_")

    def test_junos_format(self):
        result = as_path_regex(65001, vendor="junos")
        self.assertEqual(result, "^65001 ")

    def test_unknown_vendor_defaults_cisco(self):
        result = as_path_regex(65001, vendor="unknown")
        self.assertEqual(result, "^65001_")


class IpNetworkFilterTest(TestCase):
    def test_ipv4_prefix(self):
        result = ip_network("192.0.2.0/24")
        self.assertEqual(result["network"], "192.0.2.0")
        self.assertEqual(result["prefix_length"], 24)
        self.assertEqual(result["netmask"], "255.255.255.0")

    def test_ipv6_prefix(self):
        result = ip_network("2001:db8::/32")
        self.assertEqual(result["network"], "2001:db8::")
        self.assertEqual(result["prefix_length"], 32)


class GroupByFilterTest(TestCase):
    def test_group_by_attribute(self):
        items = [
            {"name": "a", "type": "peer"},
            {"name": "b", "type": "transit"},
            {"name": "c", "type": "peer"},
        ]
        result = dict(group_by(items, "type"))
        self.assertEqual(len(result["peer"]), 2)
        self.assertEqual(len(result["transit"]), 1)

    def test_group_by_empty_list(self):
        result = dict(group_by([], "type"))
        self.assertEqual(result, {})


class ToCommunityListFilterTest(TestCase):
    def test_cisco_format(self):
        result = to_community_list("65000:100", "PEERS", vendor="cisco")
        self.assertIn("ip community-list", result)
        self.assertIn("65000:100", result)

    def test_junos_format(self):
        result = to_community_list("65000:100", "PEERS", vendor="junos")
        self.assertIn("community", result)
        self.assertIn("65000:100", result)


class ToPrefixSetFilterTest(TestCase):
    def test_cisco_format(self):
        prefixes = [
            {"prefix": "192.0.2.0/24", "le": 32, "ge": 24},
        ]
        result = to_prefix_set(prefixes, "CUSTOMERS", vendor="cisco")
        self.assertIn("ip prefix-list", result)
        self.assertIn("192.0.2.0/24", result)

    def test_junos_format(self):
        prefixes = [
            {"prefix": "192.0.2.0/24"},
        ]
        result = to_prefix_set(prefixes, "CUSTOMERS", vendor="junos")
        self.assertIn("prefix-list", result)
        self.assertIn("192.0.2.0/24", result)
```

**Step 2: Run test to verify it fails**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_jinja2_filters -v 2`
Expected: FAIL with "No module named 'netbox_peering_manager.jinja2_filters'"

**Step 3: Write minimal implementation**

```python
# netbox_peering_manager/jinja2_filters.py
"""Custom Jinja2 filters for BGP configuration templating."""

import ipaddress
from itertools import groupby as itertools_groupby

__all__ = (
    "as_path_regex",
    "group_by",
    "ip_network",
    "to_community_list",
    "to_prefix_set",
    "PEERING_FILTERS",
)


def as_path_regex(asn: int, vendor: str = "cisco") -> str:
    """Convert ASN to AS-path regex.

    Args:
        asn: The AS number
        vendor: Target vendor (cisco, junos)

    Returns:
        AS-path regex string

    Examples:
        {{ session.peer_asn | as_path_regex }} → "^65001_"
        {{ session.peer_asn | as_path_regex("junos") }} → "^65001 "
    """
    if vendor == "junos":
        return f"^{asn} "
    # Default to Cisco format
    return f"^{asn}_"


def ip_network(prefix: str) -> dict:
    """Parse IP prefix into components.

    Args:
        prefix: IP prefix string (e.g., "192.0.2.0/24")

    Returns:
        Dict with network, prefix_length, netmask (IPv4 only)

    Examples:
        {{ "192.0.2.0/24" | ip_network }}
        → {"network": "192.0.2.0", "prefix_length": 24, "netmask": "255.255.255.0"}
    """
    net = ipaddress.ip_network(prefix, strict=False)
    result = {
        "network": str(net.network_address),
        "prefix_length": net.prefixlen,
    }
    if isinstance(net, ipaddress.IPv4Network):
        result["netmask"] = str(net.netmask)
    return result


def group_by(items, attr: str):
    """Group objects by attribute.

    Args:
        items: Iterable of objects or dicts
        attr: Attribute name to group by

    Yields:
        Tuples of (key, list of items)

    Examples:
        {% for rel, sessions in sessions | group_by('relationship') %}
    """

    def get_key(item):
        if isinstance(item, dict):
            return item.get(attr)
        return getattr(item, attr, None)

    # Sort first since groupby requires sorted input
    sorted_items = sorted(items, key=get_key)
    for key, group in itertools_groupby(sorted_items, key=get_key):
        yield key, list(group)


def to_community_list(value: str, name: str, vendor: str = "cisco") -> str:
    """Convert community value to vendor community-list syntax.

    Args:
        value: Community value (e.g., "65000:100")
        name: Name for the community list
        vendor: Target vendor (cisco, junos)

    Returns:
        Vendor-specific community-list configuration

    Examples:
        {{ community.value | to_community_list("PEERS") }}
    """
    if vendor == "junos":
        return f"community {name} members {value};"
    # Default to Cisco format
    return f"ip community-list standard {name} permit {value}"


def to_prefix_set(prefixes: list, name: str, vendor: str = "cisco") -> str:
    """Convert prefix list to vendor prefix-set syntax.

    Args:
        prefixes: List of prefix dicts with 'prefix', optional 'le', 'ge'
        name: Name for the prefix list
        vendor: Target vendor (cisco, junos)

    Returns:
        Vendor-specific prefix-list configuration

    Examples:
        {{ prefix_list.rules | to_prefix_set("CUSTOMERS") }}
    """
    lines = []

    if vendor == "junos":
        lines.append(f"prefix-list {name} {{")
        for p in prefixes:
            prefix = p.get("prefix", p) if isinstance(p, dict) else str(p)
            lines.append(f"    {prefix};")
        lines.append("}")
    else:
        # Cisco format
        seq = 10
        for p in prefixes:
            if isinstance(p, dict):
                prefix = p.get("prefix", "")
                le = p.get("le")
                ge = p.get("ge")
                entry = f"ip prefix-list {name} seq {seq} permit {prefix}"
                if ge:
                    entry += f" ge {ge}"
                if le:
                    entry += f" le {le}"
            else:
                entry = f"ip prefix-list {name} seq {seq} permit {p}"
            lines.append(entry)
            seq += 10

    return "\n".join(lines)


# Dictionary of filters to register with Jinja2
PEERING_FILTERS = {
    "as_path_regex": as_path_regex,
    "ip_network": ip_network,
    "group_by": group_by,
    "to_community_list": to_community_list,
    "to_prefix_set": to_prefix_set,
}
```

**Step 4: Run test to verify it passes**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_jinja2_filters -v 2`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add netbox_peering_manager/jinja2_filters.py netbox_peering_manager/tests/test_jinja2_filters.py
git commit -m "feat: add Jinja2 filters for BGP config templating"
```

---

## Task 2: Register Jinja2 Filters in Plugin Config

**Files:**
- Modify: `netbox_peering_manager/__init__.py`

**Step 1: Write the test**

No new test file needed - we'll verify by checking settings after plugin loads.

**Step 2: Modify plugin config to register filters**

```python
# netbox_peering_manager/__init__.py
from netbox.plugins import PluginConfig

from .version import __version__


class BGPConfig(PluginConfig):
    name = "netbox_peering_manager"
    verbose_name = "BGP"
    description = "Subsystem for tracking bgp related objects"
    version = __version__
    author = "Jonathan Senecal"
    author_email = "jonathan.senecal@metrooptic.com"
    base_url = "bgp"
    required_settings = []
    min_version = "4.4.0"
    max_version = "4.4.99"
    default_settings = {
        "device_ext_page": "right",
        "top_level_menu": False,
        "peeringdb_url": None,
        "peeringdb_api_key": None,
        "peeringdb_timeout": None,
        "peeringdb_local_asns": [],
    }
    jobs = [
        "netbox_peering_manager.jobs.SyncPrefixListJob",
        "netbox_peering_manager.jobs.SyncAllPrefixListsJob",
    ]

    def ready(self):
        super().ready()
        # Import views to ensure @register_model_view decorators are executed
        # Register initializers with netbox-initializers plugin (if installed)
        import contextlib

        from . import views  # noqa: F401

        with contextlib.suppress(ImportError):
            from . import initializers  # noqa: F401

        # Register Jinja2 filters for config templating
        self._register_jinja2_filters()

    def _register_jinja2_filters(self):
        """Register custom Jinja2 filters with NetBox."""
        from django.conf import settings

        from .jinja2_filters import PEERING_FILTERS

        if not hasattr(settings, "JINJA2_FILTERS"):
            settings.JINJA2_FILTERS = {}
        settings.JINJA2_FILTERS.update(PEERING_FILTERS)


config = BGPConfig  # noqa
```

**Step 3: Run tests to verify nothing broke**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager -v 2 --parallel`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add netbox_peering_manager/__init__.py
git commit -m "feat: register Jinja2 filters on plugin load"
```

---

## Task 3: Create Config Renderer Service

**Files:**
- Create: `netbox_peering_manager/services/config_renderer.py`
- Test: `netbox_peering_manager/tests/test_config_renderer.py`

**Step 1: Write the failing test**

```python
# netbox_peering_manager/tests/test_config_renderer.py
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress

from netbox_peering_manager.models import BGPPeerGroup, BGPSession, RoutingPolicy
from netbox_peering_manager.services.config_renderer import ConfigRenderer


class ConfigRendererTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create required objects
        site = Site.objects.create(name="Test Site", slug="test-site")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Test Router", slug="test-router"
        )
        device_role = DeviceRole.objects.create(name="Router", slug="router")
        cls.device = Device.objects.create(
            name="router1",
            device_type=device_type,
            role=device_role,
            site=site,
        )
        interface = Interface.objects.create(device=cls.device, name="eth0")

        rir = RIR.objects.create(name="Test RIR", slug="test-rir")
        local_asn = ASN.objects.create(asn=65000, rir=rir)
        peer_asn = ASN.objects.create(asn=65001, rir=rir)

        local_ip = IPAddress.objects.create(address="192.0.2.1/24")
        remote_ip = IPAddress.objects.create(address="192.0.2.2/24")

        peer_group = BGPPeerGroup.objects.create(name="PEERS", slug="peers")

        import_policy = RoutingPolicy.objects.create(name="IMPORT-PEER", slug="import-peer")
        export_policy = RoutingPolicy.objects.create(name="EXPORT-PEER", slug="export-peer")

        cls.session = BGPSession.objects.create(
            name="Peer-AS65001",
            device=cls.device,
            local_address=local_ip,
            remote_address=remote_ip,
            local_as=local_asn,
            remote_as=peer_asn,
            peer_group=peer_group,
        )
        cls.session.import_policies.add(import_policy)
        cls.session.export_policies.add(export_policy)

    def test_build_context_for_device(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device)

        self.assertIn("device", context)
        self.assertIn("sessions", context)
        self.assertEqual(context["device"]["name"], "router1")
        self.assertEqual(len(context["sessions"]), 1)

    def test_build_context_for_sessions(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session])

        self.assertIn("sessions", context)
        self.assertEqual(len(context["sessions"]), 1)
        session = context["sessions"][0]
        self.assertEqual(session["name"], "Peer-AS65001")
        self.assertEqual(session["peer_asn"], 65001)

    def test_session_includes_policies(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(sessions=[self.session])

        session = context["sessions"][0]
        self.assertIn("import_policies", session)
        self.assertIn("export_policies", session)
        self.assertEqual(len(session["import_policies"]), 1)
        self.assertEqual(session["import_policies"][0]["name"], "IMPORT-PEER")

    def test_context_includes_deduplicated_objects(self):
        renderer = ConfigRenderer()
        context = renderer.build_context(device=self.device)

        self.assertIn("peer_groups", context)
        self.assertIn("routing_policies", context)
        # Peer groups should be deduplicated
        self.assertEqual(len(context["peer_groups"]), 1)

    def test_empty_device_returns_empty_sessions(self):
        site = Site.objects.create(name="Empty Site", slug="empty-site")
        manufacturer = Manufacturer.objects.get(slug="cisco")
        device_type = DeviceType.objects.get(slug="test-router")
        device_role = DeviceRole.objects.get(slug="router")
        empty_device = Device.objects.create(
            name="router2",
            device_type=device_type,
            role=device_role,
            site=site,
        )

        renderer = ConfigRenderer()
        context = renderer.build_context(device=empty_device)

        self.assertEqual(len(context["sessions"]), 0)
```

**Step 2: Run test to verify it fails**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_config_renderer -v 2`
Expected: FAIL with "No module named 'netbox_peering_manager.services.config_renderer'"

**Step 3: Write minimal implementation**

```python
# netbox_peering_manager/services/config_renderer.py
"""Config rendering service for BGP configuration templating."""

import logging
from typing import Any

from dcim.models import Device

from netbox_peering_manager.models import BGPSession

logger = logging.getLogger(__name__)


class ConfigRenderer:
    """Service for building template context and rendering BGP configurations."""

    def build_context(
        self,
        device: Device | None = None,
        sessions: list[BGPSession] | None = None,
    ) -> dict[str, Any]:
        """
        Build template context for BGP configuration rendering.

        Args:
            device: Device to render config for (fetches all sessions)
            sessions: Specific sessions to include (overrides device lookup)

        Returns:
            Dict with device, sessions, and related objects for template context
        """
        # Gather sessions
        if sessions is not None:
            session_qs = BGPSession.objects.filter(pk__in=[s.pk for s in sessions])
        elif device is not None:
            session_qs = BGPSession.objects.filter(device=device)
        else:
            session_qs = BGPSession.objects.none()

        # Prefetch related objects for efficiency
        session_qs = session_qs.select_related(
            "device",
            "local_as",
            "remote_as",
            "local_address",
            "remote_address",
            "peer_group",
            "relationship",
            "bfd",
            "peering_network",
            "peering_network__fabric",
        ).prefetch_related(
            "import_policies",
            "export_policies",
            "afi_safis",
        )

        sessions_list = list(session_qs)

        # Build context
        context = {
            "device": self._serialize_device(device) if device else None,
            "sessions": [self._serialize_session(s) for s in sessions_list],
            "peer_groups": self._collect_peer_groups(sessions_list),
            "routing_policies": self._collect_policies(sessions_list),
            "prefix_lists": self._collect_prefix_lists(sessions_list),
            "communities": self._collect_communities(sessions_list),
        }

        return context

    def _serialize_device(self, device: Device) -> dict[str, Any]:
        """Serialize device for template context."""
        return {
            "id": device.pk,
            "name": device.name,
            "platform": {
                "name": device.platform.name if device.platform else None,
                "slug": device.platform.slug if device.platform else None,
            }
            if device.platform
            else None,
            "site": {
                "name": device.site.name if device.site else None,
                "slug": device.site.slug if device.site else None,
            }
            if device.site
            else None,
        }

    def _serialize_session(self, session: BGPSession) -> dict[str, Any]:
        """Serialize BGP session for template context."""
        return {
            "id": session.pk,
            "name": session.name,
            "description": session.description,
            "status": session.status,
            "enabled": session.enabled,
            "local_asn": session.local_as.asn if session.local_as else None,
            "peer_asn": session.remote_as.asn if session.remote_as else None,
            "local_ip": str(session.local_address.address.ip) if session.local_address else None,
            "remote_ip": str(session.remote_address.address.ip) if session.remote_address else None,
            "relationship": session.relationship.name if session.relationship else None,
            "password": session.password or None,
            "multihop_ttl": session.multihop_ttl,
            "bfd_profile": self._serialize_bfd(session.bfd) if session.bfd else None,
            "peer_group": self._serialize_peer_group(session.peer_group) if session.peer_group else None,
            "peering_network": self._serialize_peering_network(session.peering_network)
            if session.peering_network
            else None,
            "import_policies": [self._serialize_policy(p) for p in session.import_policies.all()],
            "export_policies": [self._serialize_policy(p) for p in session.export_policies.all()],
            "afi_safis": [afi.afi_safi for afi in session.afi_safis.all()],
        }

    def _serialize_bfd(self, bfd) -> dict[str, Any]:
        """Serialize BFD profile for template context."""
        return {
            "name": bfd.name,
            "minimum_interval": bfd.minimum_interval,
            "multiplier": bfd.multiplier,
        }

    def _serialize_peer_group(self, peer_group) -> dict[str, Any]:
        """Serialize peer group for template context."""
        return {
            "id": peer_group.pk,
            "name": peer_group.name,
            "slug": peer_group.slug,
            "description": peer_group.description,
        }

    def _serialize_peering_network(self, network) -> dict[str, Any]:
        """Serialize peering network for template context."""
        return {
            "id": network.pk,
            "name": network.name,
            "fabric": network.fabric.name if network.fabric else None,
        }

    def _serialize_policy(self, policy) -> dict[str, Any]:
        """Serialize routing policy for template context."""
        return {
            "id": policy.pk,
            "name": policy.name,
            "slug": policy.slug,
            "description": policy.description,
            "weight": policy.weight,
            "address_family": policy.address_family,
        }

    def _collect_peer_groups(self, sessions: list[BGPSession]) -> list[dict]:
        """Collect and deduplicate peer groups from sessions."""
        seen = {}
        for session in sessions:
            if session.peer_group and session.peer_group.pk not in seen:
                seen[session.peer_group.pk] = self._serialize_peer_group(session.peer_group)
        return list(seen.values())

    def _collect_policies(self, sessions: list[BGPSession]) -> list[dict]:
        """Collect and deduplicate routing policies from sessions."""
        seen = {}
        for session in sessions:
            for policy in session.import_policies.all():
                if policy.pk not in seen:
                    seen[policy.pk] = self._serialize_policy(policy)
            for policy in session.export_policies.all():
                if policy.pk not in seen:
                    seen[policy.pk] = self._serialize_policy(policy)
        return list(seen.values())

    def _collect_prefix_lists(self, sessions: list[BGPSession]) -> list[dict]:
        """Collect prefix lists referenced by session policies."""
        # For now, return empty - will be extended when needed
        return []

    def _collect_communities(self, sessions: list[BGPSession]) -> list[dict]:
        """Collect communities referenced by session policies."""
        # For now, return empty - will be extended when needed
        return []
```

**Step 4: Run test to verify it passes**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_config_renderer -v 2`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add netbox_peering_manager/services/config_renderer.py netbox_peering_manager/tests/test_config_renderer.py
git commit -m "feat: add ConfigRenderer service for building template context"
```

---

## Task 4: Create Render Config API Serializer

**Files:**
- Modify: `netbox_peering_manager/api/serializers.py`

**Step 1: Add request serializer for render endpoint**

Add to the end of `netbox_peering_manager/api/serializers.py`:

```python
# Request serializer for render-config endpoint
class RenderConfigRequestSerializer(serializers.Serializer):
    """Serializer for render-config API request."""

    template = serializers.PrimaryKeyRelatedField(
        queryset=ConfigTemplate.objects.all(),
        help_text="ID of the ConfigTemplate to render",
    )
    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(),
        required=False,
        allow_null=True,
        help_text="ID of the device to render config for",
    )
    sessions = serializers.PrimaryKeyRelatedField(
        queryset=BGPSession.objects.all(),
        many=True,
        required=False,
        help_text="List of BGP session IDs to include",
    )

    def validate(self, data):
        """Ensure at least device or sessions is provided."""
        if not data.get("device") and not data.get("sessions"):
            raise serializers.ValidationError(
                "Either 'device' or 'sessions' must be provided."
            )
        return data
```

Also add imports at the top of the file:

```python
from dcim.models import Device
from extras.models import ConfigTemplate
```

**Step 2: Run existing tests to verify nothing broke**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_api -v 2`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add netbox_peering_manager/api/serializers.py
git commit -m "feat: add RenderConfigRequestSerializer for render endpoint"
```

---

## Task 5: Create Render Config API View

**Files:**
- Modify: `netbox_peering_manager/api/views.py`
- Test: Add to `netbox_peering_manager/tests/test_api.py`

**Step 1: Write the failing test**

Add to `netbox_peering_manager/tests/test_api.py`:

```python
from extras.models import ConfigTemplate


class RenderConfigAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create required objects
        site = Site.objects.create(name="Test Site", slug="test-site-render")
        manufacturer = Manufacturer.objects.create(name="Juniper", slug="juniper")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="MX480", slug="mx480"
        )
        device_role = DeviceRole.objects.create(name="PE Router", slug="pe-router")
        cls.device = Device.objects.create(
            name="pe1",
            device_type=device_type,
            role=device_role,
            site=site,
        )

        rir = RIR.objects.create(name="RIPE NCC", slug="ripe-ncc")
        local_asn = ASN.objects.create(asn=65000, rir=rir)
        peer_asn = ASN.objects.create(asn=65001, rir=rir)

        local_ip = IPAddress.objects.create(address="10.0.0.1/30")
        remote_ip = IPAddress.objects.create(address="10.0.0.2/30")

        cls.session = BGPSession.objects.create(
            name="Transit-Provider",
            device=cls.device,
            local_address=local_ip,
            remote_address=remote_ip,
            local_as=local_asn,
            remote_as=peer_asn,
        )

        cls.template = ConfigTemplate.objects.create(
            name="Test BGP Template",
            template_code="""
{%- for session in sessions %}
neighbor {{ session.remote_ip }} remote-as {{ session.peer_asn }}
{%- endfor %}
""".strip(),
        )

    def test_render_config_with_device(self):
        url = reverse("plugins-api:netbox_peering_manager-api:render_config")
        data = {
            "template": self.template.pk,
            "device": self.device.pk,
        }
        response = self.client.post(url, data, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.data)
        self.assertIn("neighbor 10.0.0.2 remote-as 65001", response.data["content"])

    def test_render_config_with_sessions(self):
        url = reverse("plugins-api:netbox_peering_manager-api:render_config")
        data = {
            "template": self.template.pk,
            "sessions": [self.session.pk],
        }
        response = self.client.post(url, data, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.data)

    def test_render_config_missing_params(self):
        url = reverse("plugins-api:netbox_peering_manager-api:render_config")
        data = {
            "template": self.template.pk,
        }
        response = self.client.post(url, data, format="json", **self.header)
        self.assertEqual(response.status_code, 400)

    def test_render_config_include_context(self):
        url = reverse("plugins-api:netbox_peering_manager-api:render_config")
        data = {
            "template": self.template.pk,
            "device": self.device.pk,
        }
        response = self.client.post(f"{url}?include_context=true", data, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn("context", response.data)
        self.assertIn("sessions", response.data["context"])
```

**Step 2: Run test to verify it fails**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_api.RenderConfigAPITest -v 2`
Expected: FAIL with "Reverse not found"

**Step 3: Write the view implementation**

Add to `netbox_peering_manager/api/views.py`:

```python
from extras.api.mixins import ConfigTemplateRenderMixin
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox.api.renderers import TextRenderer

from netbox_peering_manager.services.config_renderer import ConfigRenderer

from .serializers import RenderConfigRequestSerializer


class RenderConfigView(ConfigTemplateRenderMixin, APIView):
    """
    Render a ConfigTemplate with BGP session context.

    POST /api/plugins/peering-manager/render-config/
    """

    renderer_classes = [JSONRenderer, TextRenderer]

    def post(self, request):
        serializer = RenderConfigRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        template = serializer.validated_data["template"]
        device = serializer.validated_data.get("device")
        sessions = serializer.validated_data.get("sessions", [])

        # Build context
        renderer = ConfigRenderer()
        context = renderer.build_context(
            device=device,
            sessions=sessions if sessions else None,
        )

        # Render template
        response = self.render_configtemplate(request, template, context)

        # Add context to response if requested
        if request.query_params.get("include_context") == "true":
            if isinstance(response.data, dict):
                response.data["context"] = context

        # Add metadata
        if isinstance(response.data, dict):
            if device:
                response.data["device"] = {"id": device.pk, "name": device.name}
            response.data["session_count"] = len(context["sessions"])

        return response
```

**Step 4: Add URL route**

Modify `netbox_peering_manager/api/urls.py`:

```python
from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from .views import (
    # ... existing imports ...
    RenderConfigView,
)

router = NetBoxRouter()
# ... existing router registrations ...

urlpatterns = [
    path("render-config/", RenderConfigView.as_view(), name="render_config"),
    path("", include(router.urls)),
]
```

**Step 5: Run test to verify it passes**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager.tests.test_api.RenderConfigAPITest -v 2`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add netbox_peering_manager/api/views.py netbox_peering_manager/api/urls.py netbox_peering_manager/tests/test_api.py
git commit -m "feat: add render-config API endpoint"
```

---

## Task 6: Create Example Templates Documentation

**Files:**
- Create: `docs/examples/templates/junos-bgp.j2`
- Create: `docs/examples/templates/ios-xr-bgp.j2`
- Create: `docs/examples/templates/eos-bgp.j2`
- Create: `docs/examples/templates/nokia-sros-bgp.j2`

**Step 1: Create Junos example template**

```jinja2
{# docs/examples/templates/junos-bgp.j2 #}
{# Juniper Junos BGP Configuration Template #}
{# Context: device, sessions, peer_groups, routing_policies #}

groups {
    BGP-SESSIONS {
{% for session in sessions %}
        neighbor {{ session.remote_ip }} {
            description "{{ session.name }}";
            peer-as {{ session.peer_asn }};
{% if session.password %}
            authentication-key "{{ session.password }}";
{% endif %}
{% if session.multihop_ttl %}
            multihop ttl {{ session.multihop_ttl }};
{% endif %}
{% if session.bfd_profile %}
            bfd-liveness-detection {
                minimum-interval {{ session.bfd_profile.minimum_interval }};
                multiplier {{ session.bfd_profile.multiplier }};
            }
{% endif %}
{% for policy in session.import_policies | sort(attribute='weight', reverse=True) %}
            import {{ policy.name }};
{% endfor %}
{% for policy in session.export_policies | sort(attribute='weight', reverse=True) %}
            export {{ policy.name }};
{% endfor %}
        }
{% endfor %}
    }
}
```

**Step 2: Create IOS-XR example template**

```jinja2
{# docs/examples/templates/ios-xr-bgp.j2 #}
{# Cisco IOS-XR BGP Configuration Template #}
{# Context: device, sessions, peer_groups, routing_policies #}

router bgp {{ sessions[0].local_asn if sessions else 65000 }}
{% for session in sessions %}
 neighbor {{ session.remote_ip }}
  remote-as {{ session.peer_asn }}
  description {{ session.name }}
{% if session.password %}
  password clear {{ session.password }}
{% endif %}
{% if session.multihop_ttl %}
  ebgp-multihop {{ session.multihop_ttl }}
{% endif %}
{% if session.bfd_profile %}
  bfd fast-detect
  bfd minimum-interval {{ session.bfd_profile.minimum_interval }}
  bfd multiplier {{ session.bfd_profile.multiplier }}
{% endif %}
  address-family ipv4 unicast
{% for policy in session.import_policies %}
   route-policy {{ policy.name }} in
{% endfor %}
{% for policy in session.export_policies %}
   route-policy {{ policy.name }} out
{% endfor %}
  !
 !
{% endfor %}
!
```

**Step 3: Create EOS example template**

```jinja2
{# docs/examples/templates/eos-bgp.j2 #}
{# Arista EOS BGP Configuration Template #}
{# Context: device, sessions, peer_groups, routing_policies #}

router bgp {{ sessions[0].local_asn if sessions else 65000 }}
{% for session in sessions %}
   neighbor {{ session.remote_ip }} remote-as {{ session.peer_asn }}
   neighbor {{ session.remote_ip }} description {{ session.name }}
{% if session.password %}
   neighbor {{ session.remote_ip }} password {{ session.password }}
{% endif %}
{% if session.multihop_ttl %}
   neighbor {{ session.remote_ip }} ebgp-multihop {{ session.multihop_ttl }}
{% endif %}
{% if session.bfd_profile %}
   neighbor {{ session.remote_ip }} bfd
{% endif %}
{% for policy in session.import_policies %}
   neighbor {{ session.remote_ip }} route-map {{ policy.name }} in
{% endfor %}
{% for policy in session.export_policies %}
   neighbor {{ session.remote_ip }} route-map {{ policy.name }} out
{% endfor %}
{% endfor %}
```

**Step 4: Create Nokia SR OS example template**

```jinja2
{# docs/examples/templates/nokia-sros-bgp.j2 #}
{# Nokia SR OS BGP Configuration Template #}
{# Context: device, sessions, peer_groups, routing_policies #}

configure {
    router "Base" {
        bgp {
            admin-state enable
{% for session in sessions %}
            neighbor "{{ session.remote_ip }}" {
                description "{{ session.name }}"
                peer-as {{ session.peer_asn }}
{% if session.password %}
                authentication-key "{{ session.password }}"
{% endif %}
{% if session.multihop_ttl %}
                multihop {{ session.multihop_ttl }}
{% endif %}
{% if session.bfd_profile %}
                bfd-enable true
{% endif %}
                family {
                    ipv4 true
                }
{% for policy in session.import_policies %}
                import {
                    policy ["{{ policy.name }}"]
                }
{% endfor %}
{% for policy in session.export_policies %}
                export {
                    policy ["{{ policy.name }}"]
                }
{% endfor %}
            }
{% endfor %}
        }
    }
}
```

**Step 5: Commit**

```bash
mkdir -p docs/examples/templates
git add docs/examples/templates/
git commit -m "docs: add example BGP config templates for major vendors"
```

---

## Task 7: Update Feature Gap Analysis Documentation

**Files:**
- Modify: `docs/FEATURE_GAP_ANALYSIS.md`

**Step 1: Update Phase 5 status to completed**

Update the Configuration Templating section to mark it as completed with implementation details.

**Step 2: Commit**

```bash
git add docs/FEATURE_GAP_ANALYSIS.md
git commit -m "docs: mark Phase 5 Configuration Templating as completed"
```

---

## Task 8: Final Verification

**Step 1: Run all tests**

Run: `python /opt/netbox/netbox/manage.py test netbox_peering_manager -v 2 --parallel`
Expected: All tests PASS

**Step 2: Verify filters work in templates**

Create a quick manual test:

```python
# Run in Django shell: python /opt/netbox/netbox/manage.py shell
from extras.models import ConfigTemplate

template = ConfigTemplate(
    name="Test",
    template_code="{{ 65001 | as_path_regex }}"
)
result = template.render(context={})
print(result)  # Should print: ^65001_
```

**Step 3: Push to origin**

```bash
git push origin develop
```

---

## Summary

**Files created:**
- `netbox_peering_manager/jinja2_filters.py` - Custom Jinja2 filters
- `netbox_peering_manager/services/config_renderer.py` - Context builder service
- `netbox_peering_manager/tests/test_jinja2_filters.py` - Filter tests
- `netbox_peering_manager/tests/test_config_renderer.py` - Renderer tests
- `docs/examples/templates/*.j2` - Example templates

**Files modified:**
- `netbox_peering_manager/__init__.py` - Register filters
- `netbox_peering_manager/api/views.py` - Add RenderConfigView
- `netbox_peering_manager/api/urls.py` - Add render-config route
- `netbox_peering_manager/api/serializers.py` - Add request serializer
- `netbox_peering_manager/tests/test_api.py` - Add API tests
- `docs/FEATURE_GAP_ANALYSIS.md` - Update status

**API endpoint:**
- `POST /api/plugins/bgp/render-config/` - Render BGP config with template

**Jinja2 filters registered:**
- `as_path_regex` - ASN to AS-path regex
- `ip_network` - Parse prefix
- `group_by` - Group objects by attribute
- `to_community_list` - Community to vendor syntax
- `to_prefix_set` - Prefix list to vendor syntax
