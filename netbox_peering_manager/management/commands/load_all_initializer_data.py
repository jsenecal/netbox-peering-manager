"""
Extended load_initializer_data command that also loads plugin initializers.

This wraps the netbox-initializers command and additionally runs any
initializers registered by plugins that aren't in the core INITIALIZER_ORDER.
"""

import traceback

from django.core.management.base import CommandError
from netbox_initializers.initializers.base import INITIALIZER_ORDER, INITIALIZER_REGISTRY
from netbox_initializers.management.commands.load_initializer_data import (
    Command as BaseCommand,
)


class Command(BaseCommand):
    help = "Load data from YAML files into Netbox (including plugin initializers)"

    def handle(self, *args, **options):
        # Run the base command first (core NetBox initializers)
        super().handle(*args, **options)

        # Now run any plugin initializers not in INITIALIZER_ORDER
        target_path = options["path"]
        plugin_initializers = [
            name for name in INITIALIZER_REGISTRY if name not in INITIALIZER_ORDER
        ]

        # Define order for plugin initializers (dependencies first)
        plugin_order = [
            "peering_manager_relationships",
            "peering_manager_bfd",
            "peering_manager_communities",
            "peering_manager_prefix_lists",
            "peering_manager_routing_policies",
            "peering_manager_peer_groups",
            "peering_manager_sessions",
        ]

        # Sort by plugin_order, then alphabetically for unknown initializers
        def sort_key(name):
            try:
                return (0, plugin_order.index(name))
            except ValueError:
                return (1, name)

        for initializer_name in sorted(plugin_initializers, key=sort_key):
            initializer = INITIALIZER_REGISTRY[initializer_name]
            initializer_instance = initializer(target_path)
            try:
                initializer_instance.load_data()
            except Exception as e:
                traceback.print_exception(e)
                msg = f"{initializer.__name__} failed."
                raise CommandError(msg) from e
