import logging

from netbox.plugins import PluginConfig

from .version import __version__

logger = logging.getLogger(__name__)


class PeeringManagerConfig(PluginConfig):
    name = "netbox_peering_manager"
    verbose_name = "Peering Manager"
    description = "Peering management for NetBox, built on netbox-routing"
    version = __version__
    author = "Jonathan Senecal"
    author_email = "jonathan.senecal@metrooptic.com"
    base_url = "peering-manager"
    required_settings = []
    min_version = "4.6.0"
    max_version = "4.7.99"
    required_plugins = ["netbox_routing"]
    default_settings = {
        "top_level_menu": True,
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

        self._register_jinja_filters()
        logger.info("%s plugin loaded", self.name)

    def _register_jinja_filters(self):
        """Make the plugin's Jinja filters available to NetBox template rendering.

        NetBox 4.7 added register_jinja_filters(), a supported plugin API that keeps
        plugin filters in the plugin registry, below the instance-level JINJA_FILTERS
        so an administrator can always override them. NetBox 4.6 offers no such
        API, so there the filters are written straight into JINJA2_FILTERS, the
        settings dict its render_jinja2() reads and that NetBox always defines.
        """
        from .jinja2_filters import PEERING_FILTERS

        try:
            from netbox.plugins.registration import register_jinja_filters
        except ImportError:
            from django.conf import settings

            settings.JINJA2_FILTERS.update(PEERING_FILTERS)
        else:
            register_jinja_filters(PEERING_FILTERS)


config = PeeringManagerConfig  # noqa
