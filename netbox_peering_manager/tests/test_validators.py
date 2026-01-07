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
