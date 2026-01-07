from django.test import TestCase

from netbox_peering_manager.forms import CommunityForm
from netbox_peering_manager.validators import MSG_INVALID_FORMAT


class TestCommunityFormCase(TestCase):
    def test_asn_invalid_letters(self):
        form = CommunityForm(data={"value": "dsad", "status": "active"})
        self.assertEqual(form.errors["value"], [MSG_INVALID_FORMAT])

    def test_community_valid(self):
        form = CommunityForm(data={"value": "1234:5678", "status": "active"})
        self.assertEqual(form.errors.get("value"), None)
