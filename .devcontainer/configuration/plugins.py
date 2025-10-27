"""
Plugin related config
"""

PLUGINS = [
    # "netbox_initializers",  # Loads demo data
    "netbox_peering_manager",
]

PLUGINS_CONFIG = {  # type: ignore
    # "netbox_initializers": {},
    "netbox_peering_manager": {
        "top_level_menu": True,
        "device_ext_page": "tab",
    },
}
