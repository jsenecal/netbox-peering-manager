from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.text import slugify

from netbox.views import generic
from ipam.models import ASN

from .models import Community, BGPSession, RoutingPolicy, BGPPeerGroup, RoutingPolicyRule, PrefixList, PrefixListRule

from . import forms, tables, filters


class CommunityListView(generic.ObjectListView):
    queryset = Community.objects.all()
    filterset = filters.CommunityFilterSet
    filterset_form = forms.CommunityFilterForm
    table = tables.CommunityTable
    action_buttons = ("add",)


class CommunityView(generic.ObjectView):
    queryset = Community.objects.all()
    template_name = "netbox_peering_manager/community.html"


class CommunityEditView(generic.ObjectEditView):
    queryset = Community.objects.all()
    form = forms.CommunityForm


class CommunityBulkDeleteView(generic.BulkDeleteView):
    queryset = Community.objects.all()
    table = tables.CommunityTable


class CommunityBulkEditView(generic.BulkEditView):
    queryset = Community.objects.all()
    filterset = filters.CommunityFilterSet
    table = tables.CommunityTable
    form = forms.CommunityBulkEditForm


class CommunityDeleteView(generic.ObjectDeleteView):
    queryset = Community.objects.all()
    default_return_url = "plugins:netbox_peering_manager:community_list"


class CommunityBulkImportView(generic.BulkImportView):
    queryset = Community.objects.all()
    model_form = forms.CommunityImportForm


# Session


class BGPSessionListView(generic.ObjectListView):
    queryset = BGPSession.objects.all()
    filterset = filters.BGPSessionFilterSet
    filterset_form = forms.BGPSessionFilterForm
    table = tables.BGPSessionTable
    action_buttons = ("add",)


class BGPSessionEditView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionForm


class BGPSessionAddView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionAddForm


class BGPSessionBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPSession.objects.all()
    table = tables.BGPSessionTable


class BGPSessionView(generic.ObjectView):
    queryset = BGPSession.objects.all()
    template_name = "netbox_peering_manager/bgpsession.html"

    def get_extra_context(self, request, instance):
        import_policies_qs = instance.import_policies.all()
        if not import_policies_qs and instance.peer_group:
            import_policies_qs = instance.peer_group.import_policies.all()
        export_policies_qs = instance.export_policies.all()
        if not export_policies_qs and instance.peer_group:
            export_policies_qs = instance.peer_group.export_policies.all()

        import_policies_table = tables.RoutingPolicyTable(import_policies_qs, orderable=False)
        export_policies_table = tables.RoutingPolicyTable(export_policies_qs, orderable=False)

        return {"import_policies_table": import_policies_table, "export_policies_table": export_policies_table}


class BGPSessionDeleteView(generic.ObjectDeleteView):
    queryset = BGPSession.objects.all()
    default_return_url = "plugins:netbox_peering_manager:bgpsession_list"


# Routing Policy


class RoutingPolicyListView(generic.ObjectListView):
    queryset = RoutingPolicy.objects.all()
    filterset = filters.RoutingPolicyFilterSet
    filterset_form = forms.RoutingPolicyFilterForm
    table = tables.RoutingPolicyTable
    action_buttons = ("add",)


class RoutingPolicyEditView(generic.ObjectEditView):
    queryset = RoutingPolicy.objects.all()
    form = forms.RoutingPolicyForm


class RoutingPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = RoutingPolicy.objects.all()
    table = tables.RoutingPolicyTable


class RoutingPolicyView(generic.ObjectView):
    queryset = RoutingPolicy.objects.all()
    template_name = "netbox_peering_manager/routingpolicy.html"

    def get_extra_context(self, request, instance):
        sess = BGPSession.objects.filter(
            Q(import_policies=instance)
            | Q(export_policies=instance)
            | Q(peer_group__in=instance.group_import_policies.all())
            | Q(peer_group__in=instance.group_export_policies.all())
        )
        sess = sess.distinct()
        sess_table = tables.BGPSessionTable(sess)
        rules = instance.rules.all()
        rules_table = tables.RoutingPolicyRuleTable(rules)
        return {"rules_table": rules_table, "related_session_table": sess_table}


class RoutingPolicyDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicy.objects.all()
    default_return_url = "plugins:netbox_peering_manager:routingpolicy_list"


# Peer Group


class BGPPeerGroupListView(generic.ObjectListView):
    queryset = BGPPeerGroup.objects.all()
    filterset = filters.BGPPeerGroupFilterSet
    filterset_form = forms.BGPPeerGroupFilterForm
    table = tables.BGPPeerGroupTable
    action_buttons = ("add",)


class BGPPeerGroupEditView(generic.ObjectEditView):
    queryset = BGPPeerGroup.objects.all()
    form = forms.BGPPeerGroupForm


class BGPPeerGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPPeerGroup.objects.all()
    table = tables.BGPPeerGroupTable


class BGPPeerGroupView(generic.ObjectView):
    queryset = BGPPeerGroup.objects.all()
    template_name = "netbox_peering_manager/bgppeergroup.html"

    def get_extra_context(self, request, instance):
        import_policies_table = tables.RoutingPolicyTable(instance.import_policies.all(), orderable=False)
        export_policies_table = tables.RoutingPolicyTable(instance.export_policies.all(), orderable=False)

        sess = BGPSession.objects.filter(peer_group=instance)
        sess = sess.distinct()
        sess_table = tables.BGPSessionTable(sess)
        return {
            "import_policies_table": import_policies_table,
            "export_policies_table": export_policies_table,
            "related_session_table": sess_table,
        }


class BGPPeerGroupDeleteView(generic.ObjectDeleteView):
    queryset = BGPPeerGroup.objects.all()
    default_return_url = "plugins:netbox_peering_manager:bgppeergroup_list"


# Routing Policy Rule


class RoutingPolicyRuleEditView(generic.ObjectEditView):
    queryset = RoutingPolicyRule.objects.all()
    form = forms.RoutingPolicyRuleForm


class RoutingPolicyRuleDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicyRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:routingpolicyrule_list"


class RoutingPolicyRuleView(generic.ObjectView):
    queryset = RoutingPolicyRule.objects.all()
    template_name = "netbox_peering_manager/routingpolicyrule.html"

    def get_extra_context(self, request, instance):
        if request.GET.get("format") in ["json", "yaml"]:
            format = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.config.set("data_format", format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get("data_format", "json")
        else:
            format = "json"

        return {
            "format": format,
        }


class RoutingPolicyRuleListView(generic.ObjectListView):
    queryset = RoutingPolicyRule.objects.all()
    # filterset = RoutingPolicyRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.RoutingPolicyRuleTable
    action_buttons = ("add",)


# Prefix List


class PrefixListListView(generic.ObjectListView):
    queryset = PrefixList.objects.all()
    filterset = filters.PrefixListFilterSet
    filterset_form = forms.PrefixListFilterForm
    table = tables.PrefixListTable
    action_buttons = ("add",)


class PrefixListEditView(generic.ObjectEditView):
    queryset = PrefixList.objects.all()
    form = forms.PrefixListForm


class PrefixListBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixList.objects.all()
    table = tables.PrefixListTable


class PrefixListView(generic.ObjectView):
    queryset = PrefixList.objects.all()
    template_name = "netbox_peering_manager/prefixlist.html"

    def get_extra_context(self, request, instance):
        rprules = instance.plrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.prefrules.all()
        rules_table = tables.PrefixListRuleTable(rules)
        return {"rules_table": rules_table, "rprules_table": rprules_table}


class PrefixListDeleteView(generic.ObjectDeleteView):
    queryset = PrefixList.objects.all()
    default_return_url = "plugins:netbox_peering_manager:prefixlist_list"


# Prefix List Rule


class PrefixListRuleListView(generic.ObjectListView):
    queryset = PrefixListRule.objects.all()
    # filterset = RoutingPolicyRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.PrefixListRuleTable
    action_buttons = ("add",)


class PrefixListRuleEditView(generic.ObjectEditView):
    queryset = PrefixListRule.objects.all()
    form = forms.PrefixListRuleForm


class PrefixListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixListRule.objects.all()
    table = tables.PrefixListRuleTable


class PrefixListRuleDeleteView(generic.ObjectDeleteView):
    queryset = PrefixListRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:prefixlistrule_list"


class PrefixListRuleView(generic.ObjectView):
    queryset = PrefixListRule.objects.all()
    template_name = "netbox_peering_manager/prefixlistrule.html"
