"""
Plugin related config
"""

PLUGINS = [
    "netbox_routing",
    "netbox_peering_manager",
]

PLUGINS_CONFIG = {  # type: ignore
    "netbox_peering_manager": {
        "top_level_menu": True,
    },
}
