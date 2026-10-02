"""Tests for the names the plugin publishes: URL prefixes and GraphQL type names."""

from django.apps import apps
from django.test import TestCase
from django.urls import reverse
from netbox.graphql.schema import schema
from netbox.models import NetBoxModel


class PublishedNamesTestCase(TestCase):
    """The plugin is a peering manager; nothing it publishes should call it BGP."""

    def test_urls_live_under_the_plugin_slug(self):
        """UI and REST API paths are rooted at the plugin's own slug."""
        self.assertEqual(
            reverse("plugins:netbox_peering_manager:peeringsession_list"),
            "/plugins/peering-manager/peering-session/",
        )
        self.assertEqual(
            reverse("plugins-api:netbox_peering_manager-api:api-root"),
            "/api/plugins/peering-manager/",
        )

    def test_graphql_filters_are_named_after_their_model(self):
        """Each model's filter input type carries the conventional <Model>Filter name."""
        app_config = apps.get_app_config("netbox_peering_manager")
        models = [model for model in app_config.get_models() if issubclass(model, NetBoxModel)]
        self.assertTrue(models)

        for model in models:
            with self.subTest(model=model.__name__):
                self.assertIsNotNone(schema.get_type_by_name(f"{model.__name__}Filter"))
                self.assertIsNone(schema.get_type_by_name(f"NetBoxBGP{model.__name__}Filter"))

    def test_status_enum_graphql_name(self):
        """The shared status enum is published without the legacy prefix."""
        self.assertIsNotNone(schema.get_type_by_name("PeeringStatusEnum"))
        self.assertIsNone(schema.get_type_by_name("NetBoxBGPPeeringStatusEnum"))
