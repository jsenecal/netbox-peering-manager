from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_peering_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringsession_list",
        link_text="Peering Sessions",
        permissions=["netbox_peering_manager.view_peeringsession"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringsession_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peeringsession"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringsession_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peeringsession"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peerasn_list",
        link_text="Peer ASNs",
        permissions=["netbox_peering_manager.view_peerasn"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peerasn_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peerasn"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peerasn_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peerasn"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:relationship_list",
        link_text="Relationship Types",
        permissions=["netbox_peering_manager.view_relationship"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:relationship_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_relationship"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:relationship_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_relationship"],
            ),
        ),
    ),
)

_irr_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:irrsource_list",
        link_text="IRR Sources",
        permissions=["netbox_peering_manager.view_irrsource"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:irrsource_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_irrsource"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:irrsource_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_irrsource"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:irrprefixlistconfig_list",
        link_text="IRR Prefix List Configs",
        permissions=["netbox_peering_manager.view_irrprefixlistconfig"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:irrprefixlistconfig_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_irrprefixlistconfig"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:irrprefixlistconfig_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_irrprefixlistconfig"],
            ),
        ),
    ),
)

_fabrics_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringfabrictype_list",
        link_text="Fabric Types",
        permissions=["netbox_peering_manager.view_peeringfabrictype"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringfabrictype_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peeringfabrictype"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringfabrictype_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peeringfabrictype"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringfabric_list",
        link_text="Fabrics",
        permissions=["netbox_peering_manager.view_peeringfabric"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringfabric_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peeringfabric"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringfabric_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peeringfabric"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringfabric_create_from_peeringdb",
        link_text="Create from PeeringDB",
        permissions=["netbox_peering_manager.add_peeringfabric"],
        buttons=(),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringnetwork_list",
        link_text="Networks",
        permissions=["netbox_peering_manager.view_peeringnetwork"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringnetwork_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peeringnetwork"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringnetwork_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peeringnetwork"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:peeringconnection_list",
        link_text="Connections",
        permissions=["netbox_peering_manager.view_peeringconnection"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringconnection_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_peeringconnection"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:peeringconnection_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_peeringconnection"],
            ),
        ),
    ),
)

plugin_settings = settings.PLUGINS_CONFIG.get("netbox_peering_manager", {})

if plugin_settings.get("top_level_menu"):
    menu = PluginMenu(
        label="Peering",
        groups=(
            ("Peering", _peering_menu),
            ("Fabrics", _fabrics_menu),
            ("IRR", _irr_menu),
        ),
        icon_class="mdi mdi-hub",
    )
else:
    menu_items = _peering_menu + _irr_menu + _fabrics_menu
