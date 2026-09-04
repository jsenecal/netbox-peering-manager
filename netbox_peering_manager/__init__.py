import logging

from netbox.plugins import PluginConfig

from .version import __version__

logger = logging.getLogger(__name__)


class BGPConfig(PluginConfig):
    name = "netbox_peering_manager"
    verbose_name = "BGP"
    description = "Peering management for NetBox, built on netbox-routing"
    version = __version__
    author = "Jonathan Senecal"
    author_email = "jonathan.senecal@metrooptic.com"
    base_url = "bgp"
    required_settings = []
    min_version = "4.5.0"
    max_version = "4.6.99"
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
        so an administrator can always override them. Earlier releases offer no such
        API, so 4.5/4.6 fall back to writing straight into the settings dict that
        render_jinja2() reads -- JINJA_FILTERS where that name exists, and the
        pre-4.7 JINJA2_FILTERS spelling otherwise.
        """
        from .jinja2_filters import PEERING_FILTERS

        try:
            from netbox.plugins.registration import register_jinja_filters
        except ImportError:
            from django.conf import settings

            if hasattr(settings, "JINJA_FILTERS"):
                settings.JINJA_FILTERS.update(PEERING_FILTERS)
                return
            if not hasattr(settings, "JINJA2_FILTERS"):
                settings.JINJA2_FILTERS = {}
            settings.JINJA2_FILTERS.update(PEERING_FILTERS)
        else:
            register_jinja_filters(PEERING_FILTERS)


config = BGPConfig  # noqa
