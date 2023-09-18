from extras.plugins import PluginConfig
from .version import __version__


class PeeringManagerConfig(PluginConfig):
    name = "netbox_peering_manager"
    verbose_name = "NetBox Peering Manager"
    description = "Plugin to document BGP peers and related objects"
    version = __version__
    author = "Jonathan Senecal"
    author_email = "contact@jonathansenecal.com"
    base_url = "bgp"
    required_settings = []
    min_version = "3.4.0"
    max_version = "3.6.99"
    default_settings = {
        "device_ext_page": "right",
        "top_level_menu": True,
    }


config = PeeringManagerConfig  # noqa
