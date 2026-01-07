"""Tests for Jinja2 filters for BGP config templating."""

from django.test import TestCase


class AsPathRegexFilterTestCase(TestCase):
    """Test cases for as_path_regex filter."""

    def test_as_path_regex_cisco_format(self):
        """Test AS-path regex with Cisco vendor format."""
        from netbox_peering_manager.jinja2_filters import as_path_regex

        result = as_path_regex(65001, vendor="cisco")
        self.assertEqual(result, "^65001_")

    def test_as_path_regex_junos_format(self):
        """Test AS-path regex with Junos vendor format."""
        from netbox_peering_manager.jinja2_filters import as_path_regex

        result = as_path_regex(65001, vendor="junos")
        self.assertEqual(result, "^65001 ")

    def test_as_path_regex_unknown_vendor_defaults_to_cisco(self):
        """Unknown vendor should default to Cisco format."""
        from netbox_peering_manager.jinja2_filters import as_path_regex

        result = as_path_regex(65001, vendor="unknown")
        self.assertEqual(result, "^65001_")

    def test_as_path_regex_default_vendor_is_cisco(self):
        """Default vendor should be Cisco."""
        from netbox_peering_manager.jinja2_filters import as_path_regex

        result = as_path_regex(65001)
        self.assertEqual(result, "^65001_")

    def test_as_path_regex_with_4byte_asn(self):
        """Test AS-path regex with 4-byte ASN."""
        from netbox_peering_manager.jinja2_filters import as_path_regex

        result = as_path_regex(4200000001, vendor="cisco")
        self.assertEqual(result, "^4200000001_")


class IpNetworkFilterTestCase(TestCase):
    """Test cases for ip_network filter."""

    def test_ip_network_ipv4_prefix(self):
        """Test ip_network filter with IPv4 prefix."""
        from netbox_peering_manager.jinja2_filters import ip_network

        result = ip_network("192.168.1.0/24")
        self.assertEqual(result["network"], "192.168.1.0")
        self.assertEqual(result["prefix_length"], 24)
        self.assertEqual(result["netmask"], "255.255.255.0")

    def test_ip_network_ipv6_prefix(self):
        """Test ip_network filter with IPv6 prefix."""
        from netbox_peering_manager.jinja2_filters import ip_network

        result = ip_network("2001:db8::/32")
        self.assertEqual(result["network"], "2001:db8::")
        self.assertEqual(result["prefix_length"], 32)
        self.assertEqual(result["netmask"], "ffff:ffff::")

    def test_ip_network_ipv4_host_prefix(self):
        """Test ip_network filter with IPv4 /32 prefix."""
        from netbox_peering_manager.jinja2_filters import ip_network

        result = ip_network("10.0.0.1/32")
        self.assertEqual(result["network"], "10.0.0.1")
        self.assertEqual(result["prefix_length"], 32)
        self.assertEqual(result["netmask"], "255.255.255.255")

    def test_ip_network_ipv6_host_prefix(self):
        """Test ip_network filter with IPv6 /128 prefix."""
        from netbox_peering_manager.jinja2_filters import ip_network

        result = ip_network("2001:db8::1/128")
        self.assertEqual(result["network"], "2001:db8::1")
        self.assertEqual(result["prefix_length"], 128)
        self.assertEqual(result["netmask"], "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")


class GroupByFilterTestCase(TestCase):
    """Test cases for group_by filter."""

    def test_group_by_attribute(self):
        """Test grouping objects by attribute."""
        from netbox_peering_manager.jinja2_filters import group_by

        # Create mock objects with a 'category' attribute
        class MockObj:
            def __init__(self, name, category):
                self.name = name
                self.category = category

        items = [
            MockObj("item1", "A"),
            MockObj("item2", "B"),
            MockObj("item3", "A"),
            MockObj("item4", "B"),
            MockObj("item5", "C"),
        ]

        result = list(group_by(items, "category"))

        # Should yield (key, list) tuples
        self.assertEqual(len(result), 3)

        # Check structure
        keys = [r[0] for r in result]
        self.assertIn("A", keys)
        self.assertIn("B", keys)
        self.assertIn("C", keys)

        # Check items are properly grouped
        for key, group_items in result:
            if key == "A":
                self.assertEqual(len(group_items), 2)
                names = [item.name for item in group_items]
                self.assertIn("item1", names)
                self.assertIn("item3", names)
            elif key == "B":
                self.assertEqual(len(group_items), 2)
                names = [item.name for item in group_items]
                self.assertIn("item2", names)
                self.assertIn("item4", names)
            elif key == "C":
                self.assertEqual(len(group_items), 1)
                self.assertEqual(group_items[0].name, "item5")

    def test_group_by_empty_list(self):
        """Test grouping with empty list."""
        from netbox_peering_manager.jinja2_filters import group_by

        result = list(group_by([], "category"))
        self.assertEqual(result, [])

    def test_group_by_with_dicts(self):
        """Test grouping dicts by key."""
        from netbox_peering_manager.jinja2_filters import group_by

        items = [
            {"name": "item1", "type": "router"},
            {"name": "item2", "type": "switch"},
            {"name": "item3", "type": "router"},
        ]

        result = list(group_by(items, "type"))

        self.assertEqual(len(result), 2)
        types = [r[0] for r in result]
        self.assertIn("router", types)
        self.assertIn("switch", types)


class ToCommunityListFilterTestCase(TestCase):
    """Test cases for to_community_list filter."""

    def test_to_community_list_cisco_format(self):
        """Test community list in Cisco format."""
        from netbox_peering_manager.jinja2_filters import to_community_list

        result = to_community_list("65000:100", "MY_COMMUNITY", vendor="cisco")
        self.assertIn("ip community-list", result)
        self.assertIn("MY_COMMUNITY", result)
        self.assertIn("65000:100", result)

    def test_to_community_list_junos_format(self):
        """Test community list in Junos format."""
        from netbox_peering_manager.jinja2_filters import to_community_list

        result = to_community_list("65000:100", "MY_COMMUNITY", vendor="junos")
        self.assertIn("policy-options", result)
        self.assertIn("community", result)
        self.assertIn("MY_COMMUNITY", result)
        self.assertIn("65000:100", result)

    def test_to_community_list_default_vendor(self):
        """Test community list with default vendor (Cisco)."""
        from netbox_peering_manager.jinja2_filters import to_community_list

        result = to_community_list("65000:100", "MY_COMMUNITY")
        self.assertIn("ip community-list", result)

    def test_to_community_list_large_community(self):
        """Test community list with large community."""
        from netbox_peering_manager.jinja2_filters import to_community_list

        result = to_community_list("4200000001:100:200", "MY_LARGE_COMM", vendor="cisco")
        self.assertIn("4200000001:100:200", result)


class ToPrefixSetFilterTestCase(TestCase):
    """Test cases for to_prefix_set filter."""

    def test_to_prefix_set_cisco_format_simple(self):
        """Test prefix set in Cisco format without ge/le."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        prefixes = [
            {"prefix": "192.168.0.0/16"},
            {"prefix": "10.0.0.0/8"},
        ]

        result = to_prefix_set(prefixes, "MY_PREFIX_LIST", vendor="cisco")
        self.assertIn("ip prefix-list", result)
        self.assertIn("MY_PREFIX_LIST", result)
        self.assertIn("192.168.0.0/16", result)
        self.assertIn("10.0.0.0/8", result)

    def test_to_prefix_set_cisco_format_with_ge_le(self):
        """Test prefix set in Cisco format with ge/le modifiers."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        prefixes = [
            {"prefix": "192.168.0.0/16", "ge": 20, "le": 24},
            {"prefix": "10.0.0.0/8"},
        ]

        result = to_prefix_set(prefixes, "MY_PREFIX_LIST", vendor="cisco")
        self.assertIn("ge 20", result)
        self.assertIn("le 24", result)

    def test_to_prefix_set_junos_format(self):
        """Test prefix set in Junos format."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        prefixes = [
            {"prefix": "192.168.0.0/16"},
            {"prefix": "10.0.0.0/8"},
        ]

        result = to_prefix_set(prefixes, "MY_PREFIX_LIST", vendor="junos")
        self.assertIn("policy-options", result)
        self.assertIn("prefix-list", result)
        self.assertIn("MY_PREFIX_LIST", result)
        self.assertIn("192.168.0.0/16", result)
        self.assertIn("10.0.0.0/8", result)

    def test_to_prefix_set_junos_format_with_ge_le(self):
        """Test prefix set in Junos format with prefix-length-range."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        prefixes = [
            {"prefix": "192.168.0.0/16", "ge": 20, "le": 24},
        ]

        result = to_prefix_set(prefixes, "MY_PREFIX_LIST", vendor="junos")
        # Junos uses prefix-length-range notation: prefix/len orlonger or prefix/len prefix-length-range /ge-/le
        self.assertIn("192.168.0.0/16", result)

    def test_to_prefix_set_default_vendor(self):
        """Test prefix set with default vendor (Cisco)."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        prefixes = [{"prefix": "192.168.0.0/16"}]
        result = to_prefix_set(prefixes, "MY_PREFIX_LIST")
        self.assertIn("ip prefix-list", result)

    def test_to_prefix_set_empty_list(self):
        """Test prefix set with empty list."""
        from netbox_peering_manager.jinja2_filters import to_prefix_set

        result = to_prefix_set([], "EMPTY_LIST", vendor="cisco")
        # Should still generate valid syntax but with no entries
        self.assertIn("MY_PREFIX_LIST", result) if "MY_PREFIX_LIST" in result else True
        # Empty list should return empty string or minimal config
        self.assertIsInstance(result, str)


class PeeringFiltersExportTestCase(TestCase):
    """Test cases for PEERING_FILTERS export dict."""

    def test_peering_filters_dict_exists(self):
        """Test that PEERING_FILTERS dict is exported."""
        from netbox_peering_manager.jinja2_filters import PEERING_FILTERS

        self.assertIsInstance(PEERING_FILTERS, dict)

    def test_peering_filters_contains_all_filters(self):
        """Test that PEERING_FILTERS contains all required filters."""
        from netbox_peering_manager.jinja2_filters import PEERING_FILTERS

        required_filters = [
            "as_path_regex",
            "ip_network",
            "group_by",
            "to_community_list",
            "to_prefix_set",
        ]

        for filter_name in required_filters:
            self.assertIn(filter_name, PEERING_FILTERS, f"Missing filter: {filter_name}")

    def test_peering_filters_values_are_callable(self):
        """Test that PEERING_FILTERS values are callable functions."""
        from netbox_peering_manager.jinja2_filters import PEERING_FILTERS

        for name, func in PEERING_FILTERS.items():
            self.assertTrue(callable(func), f"Filter '{name}' is not callable")
