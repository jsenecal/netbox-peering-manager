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


config = BGPConfig  # noqa
