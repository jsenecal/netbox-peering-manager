from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_menu_items_primary = (
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
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bfd_list",
        link_text="BFD Profiles",
        permissions=["netbox_peering_manager.view_bfd"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bfd_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bfd"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bfd_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_bfd"],
            ),
        ),
    ),
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
        link="plugins:netbox_peering_manager:community_list",
        link_text="Communities",
        permissions=["netbox_peering_manager.view_community"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:community_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_community"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:community_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_community"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:communitylist_list",
        link_text="Community Lists",
        permissions=["netbox_peering_manager.view_communitylist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:communitylist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_communitylist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:communitylist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_communitylist"],
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
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bgpsession"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgpsession_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
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
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_routingpolicy"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicy_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_routingpolicy"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:routingpolicyrule_list",
        link_text="Routing Policy Rules",
        permissions=["netbox_peering_manager.view_routingpolicyrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicyrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_routingpolicyrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicyrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_routingpolicyrule"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:prefixlist_list",
        link_text="Prefix Lists",
        permissions=["netbox_peering_manager.view_prefixlist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_prefixlist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_prefixlist"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:prefixlistrule_list",
        link_text="Prefix List Rules",
        permissions=["netbox_peering_manager.view_prefixlistrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlistrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_prefixlistrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlistrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_prefixlistrule"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:aspathlist_list",
        link_text="AS Path Lists",
        permissions=["netbox_peering_manager.view_aspathlist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_aspathlist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_aspathlist"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:aspathlistrule_list",
        link_text="AS Path List Rules",
        permissions=["netbox_peering_manager.view_aspathlistrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlistrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_aspathlistrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlistrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_aspathlistrule"],
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
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bgppeergroup"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgppeergroup_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_bgppeergroup"],
            ),
        ),
    ),
)


_menu_items_grouped = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bgpsession_list",
        link_text="Sessions",
        permissions=["netbox_peering_manager.view_bgpsession"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgpsession_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bgpsession"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgpsession_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_bgpsession"],
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
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bgppeergroup"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bgppeergroup_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_bgppeergroup"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:community_list",
        link_text="Communities",
        permissions=["netbox_peering_manager.view_community"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:community_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_community"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:community_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_community"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:communitylist_list",
        link_text="Community Lists",
        permissions=["netbox_peering_manager.view_communitylist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:communitylist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_communitylist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:communitylist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_communitylist"],
            ),
        ),
    ),
)

_config_menu = (
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
    PluginMenuItem(
        link="plugins:netbox_peering_manager:bfd_list",
        link_text="BFD Profiles",
        permissions=["netbox_peering_manager.view_bfd"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bfd_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_bfd"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:bfd_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_bfd"],
            ),
        ),
    ),
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
)

_aspath_list_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:aspathlist_list",
        link_text="AS Path Lists",
        permissions=["netbox_peering_manager.view_aspathlist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_aspathlist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_aspathlist"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:aspathlistrule_list",
        link_text="AS Path List Rules",
        permissions=["netbox_peering_manager.view_aspathlistrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlistrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_aspathlistrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:aspathlistrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_aspathlistrule"],
            ),
        ),
    ),
)

_routing_policy_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:routingpolicy_list",
        link_text="Routing Policies",
        permissions=["netbox_peering_manager.view_routingpolicy"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicy_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_routingpolicy"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicy_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_routingpolicy"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:routingpolicyrule_list",
        link_text="Routing Policy Rules",
        permissions=["netbox_peering_manager.view_routingpolicyrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicyrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_routingpolicyrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:routingpolicyrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_routingpolicyrule"],
            ),
        ),
    ),
)


_prefix_list_menu = (
    PluginMenuItem(
        link="plugins:netbox_peering_manager:prefixlist_list",
        link_text="Prefix Lists",
        permissions=["netbox_peering_manager.view_prefixlist"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlist_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_prefixlist"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlist_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_prefixlist"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_peering_manager:prefixlistrule_list",
        link_text="Prefix List Rules",
        permissions=["netbox_peering_manager.view_prefixlistrule"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlistrule_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_peering_manager.add_prefixlistrule"],
            ),
            PluginMenuButton(
                link="plugins:netbox_peering_manager:prefixlistrule_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=["netbox_peering_manager.add_prefixlistrule"],
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
            ("BGP", _menu_items_grouped),
            ("Fabrics", _fabrics_menu),
            ("Prefix Lists", _prefix_list_menu),
            ("Routing Policies", _routing_policy_menu),
            ("AS Path Lists", _aspath_list_menu),
            ("Configuration", _config_menu),
        ),
        icon_class="mdi mdi-hub",
    )
else:
    menu_items = _menu_items_primary
