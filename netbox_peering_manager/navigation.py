from django.conf import settings

from extras.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
from utilities.choices import ButtonColorChoices

try:
    from extras.plugins import get_plugin_config  # type: ignore
except ImportError:
    from extras.plugins.utils import get_plugin_config

_bgp_menu_items = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bgpcommunity_list",
        link_text="Communities",
        permissions=["netbox_peering_manager.view_community"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgpcommunity_add",
                title="Communities",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_peering_manager.add_community"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bgpsession_list",
        link_text="Sessions",
        permissions=["netbox_peering_manager.view_bgpsession"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgpsession_add",
                title="Sessions",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_peering_manager.add_bgpsession"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:routingpolicy_list",
        link_text="Routing Policies",
        permissions=["netbox_peering_manager.view_routingpolicy"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicy_add",
                title="Routing Policies",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_peering_manager.add_routingpolicy"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bgppeergroup_list",
        link_text="Peer Groups",
        permissions=["netbox_peering_manager.view_bgppeergroup"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgppeergroup_add",
                title="Peer Groups",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_peering_manager.add_bgppeergroup"],
            ),
        ),
    ),
)
_routing_menu_items = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:prefixlist_list",
        link_text="Prefix Lists",
        permissions=["netbox_peering_manager.view_prefixlist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlist_add",
                title="Prefix Lists",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_peering_manager.add_prefixlist"],
            ),
        ),
    ),
)

if get_plugin_config("netbox_peering_manager", "top_level_menu"):
    menu = PluginMenu(
        label="Peering Manager",
        groups=(
            ("BGP", _bgp_menu_items),
            ("Routing", _routing_menu_items),
        ),
        icon_class="mdi mdi-lan",
    )
else:
    menu_items = _bgp_menu_items + _routing_menu_items
