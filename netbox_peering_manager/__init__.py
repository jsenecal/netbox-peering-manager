from netbox.plugins import PluginConfig

from .version import __version__


class BGPConfig(PluginConfig):
    name = "netbox_peering_manager"
    verbose_name = "BGP"
    description = "Subsystem for tracking bgp related objects"
    version = __version__
    author = "Nikolay Yuzefovich"
    author_email = "mgk.kolek@gmail.com"
    base_url = "bgp"
    required_settings = []
    min_version = "4.4.0"
    max_version = "4.4.99"
    default_settings = {
        "device_ext_page": "right",
        "top_level_menu": False,
    }

    def ready(self):
        super().ready()
        # Import views to ensure @register_model_view decorators are executed
        from . import views  # noqa: F401


config = BGPConfig  # noqa
