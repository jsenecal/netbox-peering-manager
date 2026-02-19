from django.test import TestCase
from ipam.models import ASN, RIR, IPAddress
from netbox_routing.models import BGPPeer, PrefixList

from netbox_peering_manager.forms import (
    IRRPrefixListConfigForm,
    IRRPrefixListConfigImportForm,
    PeeringSessionForm,
    PeeringSessionImportForm,
)
from netbox_peering_manager.models import IRRSource, Relationship


class IRRPrefixListConfigFormTestCase(TestCase):
    def setUp(self):
        self.irr_source = IRRSource.objects.create(name="Test IRR", slug="test-irr", url="http://irr.example.com/")
        self.prefix_list = PrefixList.objects.create(name="Test PL", family=4)

    def test_valid_form(self):
        form = IRRPrefixListConfigForm(
            data={
                "prefix_list": self.prefix_list.pk,
                "irr_source": self.irr_source.pk,
                "source_as_set": "AS-TEST",
                "sync_interval": 1440,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_without_irr_fields(self):
        form = IRRPrefixListConfigForm(
            data={
                "prefix_list": self.prefix_list.pk,
                "sync_interval": 1440,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class PeeringSessionFormTestCase(TestCase):
    def setUp(self):
        rir = RIR.objects.create(name="Test RIR")
        remote_asn = ASN.objects.create(asn=65001, rir=rir)
        remote_ip = IPAddress.objects.create(address="192.0.2.1/32")
        self.bgp_peer = BGPPeer.objects.create(name="test-peer", peer=remote_ip, remote_as=remote_asn)
        self.relationship = Relationship.objects.create(name="Peer", slug="peer")

    def test_valid_form(self):
        form = PeeringSessionForm(
            data={
                "bgp_peer": self.bgp_peer.pk,
                "relationship": self.relationship.pk,
                "service_reference": "TICKET-123",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_minimal(self):
        form = PeeringSessionForm(
            data={
                "bgp_peer": self.bgp_peer.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class IRRPrefixListConfigImportFormTestCase(TestCase):
    """Test CSVModelChoiceField on the IRRPrefixListConfig import form."""

    def setUp(self):
        self.irr_source = IRRSource.objects.create(name="Test IRR", slug="test-irr", url="http://irr.example.com/")
        self.prefix_list = PrefixList.objects.create(name="Import PL", family=4)

    def test_import_form_resolves_prefix_list_by_name(self):
        """prefix_list CSVModelChoiceField should resolve by name."""
        form = IRRPrefixListConfigImportForm(
            data={
                "prefix_list": "Import PL",
                "irr_source": "Test IRR",
                "source_as_set": "AS-IMPORT",
                "sync_interval": 1440,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["prefix_list"], self.prefix_list)

    def test_import_form_rejects_nonexistent_prefix_list(self):
        """Import form should reject a prefix list name that doesn't exist."""
        form = IRRPrefixListConfigImportForm(
            data={
                "prefix_list": "Nonexistent PL",
                "sync_interval": 1440,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("prefix_list", form.errors)


class PeeringSessionImportFormTestCase(TestCase):
    """Test CSVModelChoiceField on the PeeringSession import form."""

    def setUp(self):
        rir = RIR.objects.create(name="Test RIR Import")
        remote_asn = ASN.objects.create(asn=65099, rir=rir)
        remote_ip = IPAddress.objects.create(address="192.0.2.99/32")
        self.bgp_peer = BGPPeer.objects.create(name="import-peer", peer=remote_ip, remote_as=remote_asn)
        self.relationship = Relationship.objects.create(name="Transit", slug="transit")

    def test_import_form_resolves_bgp_peer_by_name(self):
        """bgp_peer CSVModelChoiceField should resolve by name."""
        form = PeeringSessionImportForm(
            data={
                "bgp_peer": "import-peer",
                "relationship": "Transit",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["bgp_peer"], self.bgp_peer)

    def test_import_form_rejects_nonexistent_bgp_peer(self):
        """Import form should reject a bgp_peer name that doesn't exist."""
        form = PeeringSessionImportForm(
            data={
                "bgp_peer": "nonexistent-peer",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("bgp_peer", form.errors)
