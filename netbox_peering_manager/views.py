from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views import View
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from virtualization.models import VirtualMachine

from . import filtersets, forms, tables
from .jobs import SyncPrefixListJob
from .models import (
    BFD,
    ASPathList,
    ASPathListRule,
    BGPPeerGroup,
    BGPSession,
    Community,
    CommunityList,
    CommunityListRule,
    IRRSource,
    PeeringConnection,
    PeeringDBPeer,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PrefixList,
    PrefixListRule,
    Relationship,
    RoutingPolicy,
    RoutingPolicyRule,
)
from .services import PeeringDBClient, PeeringDBSyncService, link_fabric_to_peeringdb

# =============================================================================
# Relationship Views
# =============================================================================


@register_model_view(Relationship, "list", path="", detail=False)
class RelationshipListView(generic.ObjectListView):
    queryset = Relationship.objects.all()
    filterset = filtersets.RelationshipFilterSet
    filterset_form = forms.RelationshipFilterForm
    table = tables.RelationshipTable


@register_model_view(Relationship)
class RelationshipView(generic.ObjectView):
    queryset = Relationship.objects.all()

    def get_extra_context(self, _request, instance):
        sessions = BGPSession.objects.filter(relationship=instance)
        sessions_table = tables.BGPSessionTable(sessions)
        return {"sessions_table": sessions_table}


@register_model_view(Relationship, "add", detail=False)
@register_model_view(Relationship, "edit")
class RelationshipEditView(generic.ObjectEditView):
    queryset = Relationship.objects.all()
    form = forms.RelationshipForm


@register_model_view(Relationship, "bulk_delete", path="delete", detail=False)
class RelationshipBulkDeleteView(generic.BulkDeleteView):
    queryset = Relationship.objects.all()
    table = tables.RelationshipTable


@register_model_view(Relationship, "bulk_edit", path="edit", detail=False)
class RelationshipBulkEditView(generic.BulkEditView):
    queryset = Relationship.objects.all()
    filterset = filtersets.RelationshipFilterSet
    table = tables.RelationshipTable
    form = forms.RelationshipBulkEditForm


@register_model_view(Relationship, "delete")
class RelationshipDeleteView(generic.ObjectDeleteView):
    queryset = Relationship.objects.all()
    default_return_url = "plugins:netbox_peering_manager:relationship_list"


@register_model_view(Relationship, "bulk_import", path="import", detail=False)
class RelationshipBulkImportView(generic.BulkImportView):
    queryset = Relationship.objects.all()
    model_form = forms.RelationshipImportForm


# =============================================================================
# BFD Views
# =============================================================================


@register_model_view(BFD, "list", path="", detail=False)
class BFDListView(generic.ObjectListView):
    queryset = BFD.objects.all()
    filterset = filtersets.BFDFilterSet
    filterset_form = forms.BFDFilterForm
    table = tables.BFDTable


@register_model_view(BFD)
class BFDView(generic.ObjectView):
    queryset = BFD.objects.all()

    def get_extra_context(self, _request, instance):
        sessions = BGPSession.objects.filter(bfd=instance)
        sessions_table = tables.BGPSessionTable(sessions)
        return {"sessions_table": sessions_table}


@register_model_view(BFD, "add", detail=False)
@register_model_view(BFD, "edit")
class BFDEditView(generic.ObjectEditView):
    queryset = BFD.objects.all()
    form = forms.BFDForm


@register_model_view(BFD, "bulk_delete", path="delete", detail=False)
class BFDBulkDeleteView(generic.BulkDeleteView):
    queryset = BFD.objects.all()
    table = tables.BFDTable


@register_model_view(BFD, "bulk_edit", path="edit", detail=False)
class BFDBulkEditView(generic.BulkEditView):
    queryset = BFD.objects.all()
    filterset = filtersets.BFDFilterSet
    table = tables.BFDTable
    form = forms.BFDBulkEditForm


@register_model_view(BFD, "delete")
class BFDDeleteView(generic.ObjectDeleteView):
    queryset = BFD.objects.all()
    default_return_url = "plugins:netbox_peering_manager:bfd_list"


@register_model_view(BFD, "bulk_import", path="import", detail=False)
class BFDBulkImportView(generic.BulkImportView):
    queryset = BFD.objects.all()
    model_form = forms.BFDImportForm


# =============================================================================
# IRRSource Views
# =============================================================================


@register_model_view(IRRSource, "list", path="", detail=False)
class IRRSourceListView(generic.ObjectListView):
    queryset = IRRSource.objects.annotate(prefix_list_count=Count("prefix_lists"))
    filterset = filtersets.IRRSourceFilterSet
    filterset_form = forms.IRRSourceFilterForm
    table = tables.IRRSourceTable


@register_model_view(IRRSource)
class IRRSourceView(generic.ObjectView):
    queryset = IRRSource.objects.all()

    def get_extra_context(self, _request, instance):
        prefix_lists = PrefixList.objects.filter(irr_source=instance)
        prefix_lists_table = tables.PrefixListTable(prefix_lists)
        return {"prefix_lists_table": prefix_lists_table}


@register_model_view(IRRSource, "add", detail=False)
@register_model_view(IRRSource, "edit")
class IRRSourceEditView(generic.ObjectEditView):
    queryset = IRRSource.objects.all()
    form = forms.IRRSourceForm


@register_model_view(IRRSource, "bulk_delete", path="delete", detail=False)
class IRRSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = IRRSource.objects.all()
    table = tables.IRRSourceTable


@register_model_view(IRRSource, "bulk_edit", path="edit", detail=False)
class IRRSourceBulkEditView(generic.BulkEditView):
    queryset = IRRSource.objects.all()
    filterset = filtersets.IRRSourceFilterSet
    table = tables.IRRSourceTable
    form = forms.IRRSourceBulkEditForm


@register_model_view(IRRSource, "delete")
class IRRSourceDeleteView(generic.ObjectDeleteView):
    queryset = IRRSource.objects.all()
    default_return_url = "plugins:netbox_peering_manager:irrsource_list"


@register_model_view(IRRSource, "bulk_import", path="import", detail=False)
class IRRSourceBulkImportView(generic.BulkImportView):
    queryset = IRRSource.objects.all()
    model_form = forms.IRRSourceImportForm


# Community


@register_model_view(Community, "list", path="", detail=False)
class CommunityListView(generic.ObjectListView):
    queryset = Community.objects.all()
    filterset = filtersets.CommunityFilterSet
    filterset_form = forms.CommunityFilterForm
    table = tables.CommunityTable


@register_model_view(Community)
class CommunityView(generic.ObjectView):
    queryset = Community.objects.all()
    template_name = "netbox_peering_manager/community.html"


@register_model_view(Community, "add", detail=False)
@register_model_view(Community, "edit")
class CommunityEditView(generic.ObjectEditView):
    queryset = Community.objects.all()
    form = forms.CommunityForm


@register_model_view(Community, "bulk_delete", path="delete", detail=False)
class CommunityBulkDeleteView(generic.BulkDeleteView):
    queryset = Community.objects.all()
    table = tables.CommunityTable


@register_model_view(Community, "bulk_edit", path="edit", detail=False)
class CommunityBulkEditView(generic.BulkEditView):
    queryset = Community.objects.all()
    filterset = filtersets.CommunityFilterSet
    table = tables.CommunityTable
    form = forms.CommunityBulkEditForm


@register_model_view(Community, "delete")
class CommunityDeleteView(generic.ObjectDeleteView):
    queryset = Community.objects.all()
    default_return_url = "plugins:netbox_peering_manager:community_list"


@register_model_view(Community, "bulk_import", path="import", detail=False)
class CommunityBulkImportView(generic.BulkImportView):
    queryset = Community.objects.all()
    model_form = forms.CommunityImportForm


# Community List


@register_model_view(CommunityList, "list", path="", detail=False)
class CommunityListListView(generic.ObjectListView):
    queryset = CommunityList.objects.all()
    filterset = filtersets.CommunityListFilterSet
    filterset_form = forms.CommunityListFilterForm
    table = tables.CommunityListTable


@register_model_view(CommunityList, "add", detail=False)
@register_model_view(CommunityList, "edit")
class CommunityListEditView(generic.ObjectEditView):
    queryset = CommunityList.objects.all()
    form = forms.CommunityListForm


@register_model_view(CommunityList, "bulk_delete", path="delete", detail=False)
class CommunityListBulkDeleteView(generic.BulkDeleteView):
    queryset = CommunityList.objects.all()
    table = tables.CommunityListTable


@register_model_view(CommunityList, "bulk_edit", path="edit", detail=False)
class CommunityListBulkEditView(generic.BulkEditView):
    queryset = CommunityList.objects.all()
    filterset = filtersets.CommunityListFilterSet
    table = tables.CommunityListTable
    form = forms.CommunityListBulkEditForm


@register_model_view(CommunityList)
class CommListView(generic.ObjectView):
    queryset = CommunityList.objects.all()
    template_name = "netbox_peering_manager/communitylist.html"

    def get_extra_context(self, _request, instance):
        rprules = instance.cmrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.commlistrules.all()
        rules_table = tables.CommunityListRuleTable(rules)
        return {"rules_table": rules_table, "rprules_table": rprules_table}


@register_model_view(CommunityList, "delete")
class CommunityListDeleteView(generic.ObjectDeleteView):
    queryset = CommunityList.objects.all()
    default_return_url = "plugins:netbox_peering_manager:communitylist_list"


@register_model_view(CommunityList, "bulk_import", path="import", detail=False)
class CommunityListBulkImportView(generic.BulkImportView):
    queryset = CommunityList.objects.all()
    model_form = forms.CommunityListImportForm


# Community List Rule


@register_model_view(CommunityListRule, "list", path="", detail=False)
class CommunityListRuleListView(generic.ObjectListView):
    queryset = CommunityListRule.objects.all()
    filterset = filtersets.CommunityListRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.CommunityListRuleTable
    actions = {"add": {"add"}, "bulk_delete": {"delete"}}


@register_model_view(CommunityListRule, "add", detail=False)
@register_model_view(CommunityListRule, "edit")
class CommunityListRuleEditView(generic.ObjectEditView):
    queryset = CommunityListRule.objects.all()
    form = forms.CommunityListRuleForm


@register_model_view(CommunityListRule, "bulk_delete", path="delete", detail=False)
class CommunityListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = CommunityListRule.objects.all()
    table = tables.CommunityListRuleTable


@register_model_view(CommunityListRule, "delete")
class CommunityListRuleDeleteView(generic.ObjectDeleteView):
    queryset = CommunityListRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:communitylistrule_list"


@register_model_view(CommunityListRule)
class CommunityListRuleView(generic.ObjectView):
    queryset = CommunityListRule.objects.all()
    template_name = "netbox_peering_manager/communitylistrule.html"


# Session


@register_model_view(BGPSession, "list", path="", detail=False)
class BGPSessionListView(generic.ObjectListView):
    queryset = BGPSession.objects.all()
    filterset = filtersets.BGPSessionFilterSet
    filterset_form = forms.BGPSessionFilterForm
    table = tables.BGPSessionTable


@register_model_view(BGPSession, "edit")
class BGPSessionEditView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionForm


@register_model_view(BGPSession, "add", detail=False)
class BGPSessionAddView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionForm


@register_model_view(BGPSession, "bulk_import", path="import", detail=False)
class BGPSessionBulkImportView(generic.BulkImportView):
    queryset = BGPSession.objects.all()
    model_form = forms.BGPSessionImportForm


@register_model_view(BGPSession, "bulk_edit", path="edit", detail=False)
class BGPSessionBulkEditView(generic.BulkEditView):
    queryset = BGPSession.objects.all()
    filterset = filtersets.BGPSessionFilterSet
    table = tables.BGPSessionTable
    form = forms.BGPSessionBulkEditForm


@register_model_view(BGPSession, "bulk_delete", path="delete", detail=False)
class BGPSessionBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPSession.objects.all()
    table = tables.BGPSessionTable


@register_model_view(BGPSession)
class BGPSessionView(generic.ObjectView):
    queryset = BGPSession.objects.all()
    template_name = "netbox_peering_manager/bgpsession.html"

    def get_extra_context(self, _request, instance):
        import_policies_qs = instance.import_policies.all()
        if not import_policies_qs and instance.peer_group:
            import_policies_qs = instance.peer_group.import_policies.all()
        export_policies_qs = instance.export_policies.all()
        if not export_policies_qs and instance.peer_group:
            export_policies_qs = instance.peer_group.export_policies.all()

        import_policies_table = tables.RoutingPolicyTable(import_policies_qs, orderable=False)
        export_policies_table = tables.RoutingPolicyTable(export_policies_qs, orderable=False)

        return {"import_policies_table": import_policies_table, "export_policies_table": export_policies_table}


@register_model_view(BGPSession, "delete")
class BGPSessionDeleteView(generic.ObjectDeleteView):
    queryset = BGPSession.objects.all()
    default_return_url = "plugins:netbox_peering_manager:bgpsession_list"


# Routing Policy


@register_model_view(RoutingPolicy, "list", path="", detail=False)
class RoutingPolicyListView(generic.ObjectListView):
    queryset = RoutingPolicy.objects.all()
    filterset = filtersets.RoutingPolicyFilterSet
    filterset_form = forms.RoutingPolicyFilterForm
    table = tables.RoutingPolicyTable


@register_model_view(RoutingPolicy, "add", detail=False)
@register_model_view(RoutingPolicy, "edit")
class RoutingPolicyEditView(generic.ObjectEditView):
    queryset = RoutingPolicy.objects.all()
    form = forms.RoutingPolicyForm


@register_model_view(RoutingPolicy, "bulk_delete", path="delete", detail=False)
class RoutingPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = RoutingPolicy.objects.all()
    table = tables.RoutingPolicyTable


@register_model_view(RoutingPolicy, "bulk_edit", path="edit", detail=False)
class RoutingPolicyBulkEditView(generic.BulkEditView):
    queryset = RoutingPolicy.objects.all()
    filterset = filtersets.RoutingPolicyFilterSet
    table = tables.RoutingPolicyTable
    form = forms.RoutingPolicyBulkEditForm


@register_model_view(RoutingPolicy)
class RoutingPolicyView(generic.ObjectView):
    queryset = RoutingPolicy.objects.all()
    template_name = "netbox_peering_manager/routingpolicy.html"

    def get_extra_context(self, _request, instance):
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


@register_model_view(RoutingPolicy, "delete")
class RoutingPolicyDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicy.objects.all()
    default_return_url = "plugins:netbox_peering_manager:routingpolicy_list"


@register_model_view(RoutingPolicy, "bulk_import", path="import", detail=False)
class RoutingPolicyBulkImportView(generic.BulkImportView):
    queryset = RoutingPolicy.objects.all()
    model_form = forms.RoutingPolicyImportForm


# Routing Policy Rule


@register_model_view(RoutingPolicyRule, "list", path="", detail=False)
class RoutingPolicyRuleListView(generic.ObjectListView):
    queryset = RoutingPolicyRule.objects.all()
    filterset = filtersets.RoutingPolicyRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.RoutingPolicyRuleTable
    actions = {"add": {"add"}, "bulk_import": {"add"}, "export": {"export"}, "bulk_delete": {"delete"}}


@register_model_view(RoutingPolicyRule, "add", detail=False)
@register_model_view(RoutingPolicyRule, "edit")
class RoutingPolicyRuleEditView(generic.ObjectEditView):
    queryset = RoutingPolicyRule.objects.all()
    form = forms.RoutingPolicyRuleForm


@register_model_view(RoutingPolicyRule, "delete")
class RoutingPolicyRuleDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicyRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:routingpolicyrule_list"


@register_model_view(RoutingPolicyRule, "bulk_delete", path="delete", detail=False)
class RoutingPolicyRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = RoutingPolicyRule.objects.all()
    table = tables.RoutingPolicyRuleTable


@register_model_view(RoutingPolicyRule)
class RoutingPolicyRuleView(generic.ObjectView):
    queryset = RoutingPolicyRule.objects.all()
    template_name = "netbox_peering_manager/routingpolicyrule.html"

    def get_extra_context(self, request, _instance):
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


@register_model_view(RoutingPolicyRule, "bulk_import", path="import", detail=False)
class RoutingPolicyRuleImportView(generic.BulkImportView):
    queryset = RoutingPolicyRule.objects.all()
    model_form = forms.RoutingPolicyRuleImportForm


# Peer Group


@register_model_view(BGPPeerGroup, "list", path="", detail=False)
class BGPPeerGroupListView(generic.ObjectListView):
    queryset = BGPPeerGroup.objects.all()
    filterset = filtersets.BGPPeerGroupFilterSet
    filterset_form = forms.BGPPeerGroupFilterForm
    table = tables.BGPPeerGroupTable


@register_model_view(BGPPeerGroup, "add", detail=False)
@register_model_view(BGPPeerGroup, "edit")
class BGPPeerGroupEditView(generic.ObjectEditView):
    queryset = BGPPeerGroup.objects.all()
    form = forms.BGPPeerGroupForm


@register_model_view(BGPPeerGroup, "bulk_delete", path="delete", detail=False)
class BGPPeerGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPPeerGroup.objects.all()
    table = tables.BGPPeerGroupTable


@register_model_view(BGPPeerGroup)
class BGPPeerGroupView(generic.ObjectView):
    queryset = BGPPeerGroup.objects.all()
    template_name = "netbox_peering_manager/bgppeergroup.html"

    def get_extra_context(self, _request, instance):
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


@register_model_view(BGPPeerGroup, "delete")
class BGPPeerGroupDeleteView(generic.ObjectDeleteView):
    queryset = BGPPeerGroup.objects.all()
    default_return_url = "plugins:netbox_peering_manager:bgppeergroup_list"


@register_model_view(BGPPeerGroup, "bulk_import", path="import", detail=False)
class BGPPeerGroupBulkImportView(generic.BulkImportView):
    queryset = BGPPeerGroup.objects.all()
    model_form = forms.BGPPeerGroupImportForm


@register_model_view(BGPPeerGroup, "bulk_edit", path="edit", detail=False)
class BGPPeerGroupBulkEditView(generic.BulkEditView):
    queryset = BGPPeerGroup.objects.all()
    filterset = filtersets.BGPPeerGroupFilterSet
    table = tables.BGPPeerGroupTable
    form = forms.BGPPeerGroupBulkEditForm


# Prefix List


@register_model_view(PrefixList, "list", path="", detail=False)
class PrefixListListView(generic.ObjectListView):
    queryset = PrefixList.objects.all()
    filterset = filtersets.PrefixListFilterSet
    filterset_form = forms.PrefixListFilterForm
    table = tables.PrefixListTable


@register_model_view(PrefixList, "add", detail=False)
@register_model_view(PrefixList, "edit")
class PrefixListEditView(generic.ObjectEditView):
    queryset = PrefixList.objects.all()
    form = forms.PrefixListForm


@register_model_view(PrefixList, "bulk_delete", path="delete", detail=False)
class PrefixListBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixList.objects.all()
    table = tables.PrefixListTable


@register_model_view(PrefixList, "bulk_edit", path="edit", detail=False)
class PrefixListBulkEditView(generic.BulkEditView):
    queryset = PrefixList.objects.all()
    filterset = filtersets.PrefixListFilterSet
    table = tables.PrefixListTable
    form = forms.PrefixListBulkEditForm


@register_model_view(PrefixList)
class PrefixListView(generic.ObjectView):
    queryset = PrefixList.objects.all()
    template_name = "netbox_peering_manager/prefixlist.html"

    def get_extra_context(self, _request, instance):
        rprules = instance.plrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.prefrules.all()
        rules_table = tables.PrefixListRuleTable(rules)

        sess = instance.session_prefix_in.all() | instance.session_prefix_out.all()
        sess_table = tables.BGPSessionTable(sess)
        return {
            "rules_table": rules_table,
            "rprules_table": rprules_table,
            "sess_table": sess_table,
        }


@register_model_view(PrefixList, "delete")
class PrefixListDeleteView(generic.ObjectDeleteView):
    queryset = PrefixList.objects.all()
    default_return_url = "plugins:netbox_peering_manager:prefixlist_list"


@register_model_view(PrefixList, "bulk_import", path="import", detail=False)
class PrefixListBulkImportView(generic.BulkImportView):
    queryset = PrefixList.objects.all()
    model_form = forms.PrefixListImportForm


@register_model_view(PrefixList, "sync", path="sync")
class PrefixListSyncView(View):
    """Trigger IRR sync for a PrefixList."""

    def post(self, request, pk):
        prefix_list = get_object_or_404(PrefixList, pk=pk)

        if not prefix_list.is_irr_managed:
            messages.error(request, "This prefix list is not IRR-managed.")
            return redirect(prefix_list.get_absolute_url())

        SyncPrefixListJob.enqueue(instance=prefix_list, user=request.user)
        messages.success(request, f"Sync job enqueued for {prefix_list.name}")
        return redirect(prefix_list.get_absolute_url())


# Prefix List Rule


@register_model_view(PrefixListRule, "list", path="", detail=False)
class PrefixListRuleListView(generic.ObjectListView):
    queryset = PrefixListRule.objects.all()
    filterset = filtersets.PrefixListRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.PrefixListRuleTable
    actions = {"add": {"add"}, "bulk_import": {"add"}, "export": {"export"}, "bulk_delete": {"delete"}}


@register_model_view(PrefixListRule, "add", detail=False)
@register_model_view(PrefixListRule, "edit")
class PrefixListRuleEditView(generic.ObjectEditView):
    queryset = PrefixListRule.objects.all()
    form = forms.PrefixListRuleForm


@register_model_view(PrefixListRule, "bulk_delete", path="delete", detail=False)
class PrefixListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixListRule.objects.all()
    table = tables.PrefixListRuleTable


@register_model_view(PrefixListRule, "delete")
class PrefixListRuleDeleteView(generic.ObjectDeleteView):
    queryset = PrefixListRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:prefixlistrule_list"


@register_model_view(PrefixListRule)
class PrefixListRuleView(generic.ObjectView):
    queryset = PrefixListRule.objects.all()
    template_name = "netbox_peering_manager/prefixlistrule.html"


@register_model_view(PrefixListRule, "bulk_import", path="import", detail=False)
class PrefixListRuleViewImportView(generic.BulkImportView):
    queryset = PrefixListRule.objects.all()
    model_form = forms.PrefixListRuleImportForm


# Viewtab for Virtual Machine


@register_model_view(VirtualMachine, name="bgpsessions", path="bgpsessions")
class VMBGPSessionView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all().prefetch_related("bgpsession_set")
    child_model = BGPSession
    table = tables.BGPSessionTable
    template_name = "generic/object_children.html"
    tab = ViewTab(label="BGP Sessions", badge=lambda obj: obj.bgpsession_set.count(), hide_if_empty=True)

    def get_children(self, _request, parent):
        return parent.bgpsession_set.all()


# AS Path List


@register_model_view(ASPathList, "list", path="", detail=False)
class ASPathListListView(generic.ObjectListView):
    queryset = ASPathList.objects.all()
    filterset = filtersets.ASPathListFilterSet
    filterset_form = forms.ASPathListFilterForm
    table = tables.ASPathListTable


@register_model_view(ASPathList, "add", detail=False)
@register_model_view(ASPathList, "edit")
class ASPathListEditView(generic.ObjectEditView):
    queryset = ASPathList.objects.all()
    form = forms.ASPathListForm


@register_model_view(ASPathList, "bulk_delete", path="delete", detail=False)
class ASPathListBulkDeleteView(generic.BulkDeleteView):
    queryset = ASPathList.objects.all()
    table = tables.ASPathListTable


@register_model_view(ASPathList, "bulk_edit", path="edit", detail=False)
class ASPathListBulkEditView(generic.BulkEditView):
    queryset = ASPathList.objects.all()
    filterset = filtersets.ASPathListFilterSet
    table = tables.ASPathListTable
    form = forms.ASPathListBulkEditForm


@register_model_view(ASPathList)
class ASPathListView(generic.ObjectView):
    queryset = ASPathList.objects.all()
    template_name = "netbox_peering_manager/aspathlist.html"

    def get_extra_context(self, _request, instance):
        rprules = instance.aspathrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.aspathlistrules.all()
        rules_table = tables.ASPathListRuleTable(rules)
        return {"rules_table": rules_table, "rprules_table": rprules_table}


@register_model_view(ASPathList, "delete")
class ASPathListDeleteView(generic.ObjectDeleteView):
    queryset = ASPathList.objects.all()
    default_return_url = "plugins:netbox_peering_manager:aspathlist_list"


@register_model_view(ASPathList, "bulk_import", path="import", detail=False)
class ASPathListBulkImportView(generic.BulkImportView):
    queryset = ASPathList.objects.all()
    model_form = forms.ASPathListImportForm


# AS Path List Rule


@register_model_view(ASPathListRule, "list", path="", detail=False)
class ASPathListRuleListView(generic.ObjectListView):
    queryset = ASPathListRule.objects.all()
    filterset = filtersets.ASPathListRuleFilterSet
    # filterset_form = ASPathListRuleFilterForm
    table = tables.ASPathListRuleTable
    actions = {"add": {"add"}, "bulk_import": {"add"}, "export": {"export"}, "bulk_delete": {"delete"}}


@register_model_view(ASPathListRule, "add", detail=False)
@register_model_view(ASPathListRule, "edit")
class ASPathListRuleEditView(generic.ObjectEditView):
    queryset = ASPathListRule.objects.all()
    form = forms.ASPathListRuleForm


@register_model_view(ASPathListRule, "bulk_delete", path="delete", detail=False)
class ASPathListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = ASPathListRule.objects.all()
    table = tables.ASPathListRuleTable


@register_model_view(ASPathListRule, "delete")
class ASPathListRuleDeleteView(generic.ObjectDeleteView):
    queryset = ASPathListRule.objects.all()
    default_return_url = "plugins:netbox_peering_manager:aspathlistrule_list"


@register_model_view(ASPathListRule, "bulk_import", path="import", detail=False)
class ASPathListRuleBulkImportView(generic.BulkImportView):
    queryset = ASPathListRule.objects.all()
    model_form = forms.ASPathListRuleImportForm


@register_model_view(ASPathListRule)
class ASPathListRuleView(generic.ObjectView):
    queryset = ASPathListRule.objects.all()
    template_name = "netbox_peering_manager/aspathlistrule.html"


# =============================================================================
# PeeringFabricType Views
# =============================================================================


@register_model_view(PeeringFabricType, "list", path="", detail=False)
class PeeringFabricTypeListView(generic.ObjectListView):
    queryset = PeeringFabricType.objects.annotate(fabric_count=Count("fabrics"))
    filterset = filtersets.PeeringFabricTypeFilterSet
    filterset_form = forms.PeeringFabricTypeFilterForm
    table = tables.PeeringFabricTypeTable


@register_model_view(PeeringFabricType)
class PeeringFabricTypeView(generic.ObjectView):
    queryset = PeeringFabricType.objects.all()

    def get_extra_context(self, _request, instance):
        fabrics = PeeringFabric.objects.filter(type=instance)
        fabrics_table = tables.PeeringFabricTable(fabrics)
        return {"fabrics_table": fabrics_table}


@register_model_view(PeeringFabricType, "add", detail=False)
@register_model_view(PeeringFabricType, "edit")
class PeeringFabricTypeEditView(generic.ObjectEditView):
    queryset = PeeringFabricType.objects.all()
    form = forms.PeeringFabricTypeForm


@register_model_view(PeeringFabricType, "bulk_delete", path="delete", detail=False)
class PeeringFabricTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = PeeringFabricType.objects.all()
    table = tables.PeeringFabricTypeTable


@register_model_view(PeeringFabricType, "bulk_edit", path="edit", detail=False)
class PeeringFabricTypeBulkEditView(generic.BulkEditView):
    queryset = PeeringFabricType.objects.all()
    filterset = filtersets.PeeringFabricTypeFilterSet
    table = tables.PeeringFabricTypeTable
    form = forms.PeeringFabricTypeBulkEditForm


@register_model_view(PeeringFabricType, "delete")
class PeeringFabricTypeDeleteView(generic.ObjectDeleteView):
    queryset = PeeringFabricType.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peeringfabrictype_list"


@register_model_view(PeeringFabricType, "bulk_import", path="import", detail=False)
class PeeringFabricTypeBulkImportView(generic.BulkImportView):
    queryset = PeeringFabricType.objects.all()
    model_form = forms.PeeringFabricTypeImportForm


# =============================================================================
# PeeringFabric Views
# =============================================================================


@register_model_view(PeeringFabric, "list", path="", detail=False)
class PeeringFabricListView(generic.ObjectListView):
    queryset = PeeringFabric.objects.annotate(network_count=Count("networks"))
    filterset = filtersets.PeeringFabricFilterSet
    filterset_form = forms.PeeringFabricFilterForm
    table = tables.PeeringFabricTable


@register_model_view(PeeringFabric)
class PeeringFabricView(generic.ObjectView):
    queryset = PeeringFabric.objects.all()

    def get_extra_context(self, _request, instance):
        networks = PeeringNetwork.objects.filter(fabric=instance)
        networks_table = tables.PeeringNetworkTable(networks)
        return {"networks_table": networks_table}


@register_model_view(PeeringFabric, "add", detail=False)
@register_model_view(PeeringFabric, "edit")
class PeeringFabricEditView(generic.ObjectEditView):
    queryset = PeeringFabric.objects.all()
    form = forms.PeeringFabricForm


@register_model_view(PeeringFabric, "bulk_delete", path="delete", detail=False)
class PeeringFabricBulkDeleteView(generic.BulkDeleteView):
    queryset = PeeringFabric.objects.all()
    table = tables.PeeringFabricTable


@register_model_view(PeeringFabric, "bulk_edit", path="edit", detail=False)
class PeeringFabricBulkEditView(generic.BulkEditView):
    queryset = PeeringFabric.objects.all()
    filterset = filtersets.PeeringFabricFilterSet
    table = tables.PeeringFabricTable
    form = forms.PeeringFabricBulkEditForm


@register_model_view(PeeringFabric, "delete")
class PeeringFabricDeleteView(generic.ObjectDeleteView):
    queryset = PeeringFabric.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peeringfabric_list"


@register_model_view(PeeringFabric, "bulk_import", path="import", detail=False)
class PeeringFabricBulkImportView(generic.BulkImportView):
    queryset = PeeringFabric.objects.all()
    model_form = forms.PeeringFabricImportForm


# =============================================================================
# PeeringNetwork Views
# =============================================================================


@register_model_view(PeeringNetwork, "list", path="", detail=False)
class PeeringNetworkListView(generic.ObjectListView):
    queryset = PeeringNetwork.objects.annotate(connection_count=Count("connections"))
    filterset = filtersets.PeeringNetworkFilterSet
    filterset_form = forms.PeeringNetworkFilterForm
    table = tables.PeeringNetworkTable


@register_model_view(PeeringNetwork)
class PeeringNetworkView(generic.ObjectView):
    queryset = PeeringNetwork.objects.all()

    def get_extra_context(self, _request, instance):
        connections = PeeringConnection.objects.filter(peering_network=instance)
        connections_table = tables.PeeringConnectionTable(connections)
        sessions = BGPSession.objects.filter(peering_network=instance)
        sessions_table = tables.BGPSessionTable(sessions)
        return {
            "connections_table": connections_table,
            "sessions_table": sessions_table,
        }


@register_model_view(PeeringNetwork, "add", detail=False)
@register_model_view(PeeringNetwork, "edit")
class PeeringNetworkEditView(generic.ObjectEditView):
    queryset = PeeringNetwork.objects.all()
    form = forms.PeeringNetworkForm


@register_model_view(PeeringNetwork, "bulk_delete", path="delete", detail=False)
class PeeringNetworkBulkDeleteView(generic.BulkDeleteView):
    queryset = PeeringNetwork.objects.all()
    table = tables.PeeringNetworkTable


@register_model_view(PeeringNetwork, "bulk_edit", path="edit", detail=False)
class PeeringNetworkBulkEditView(generic.BulkEditView):
    queryset = PeeringNetwork.objects.all()
    filterset = filtersets.PeeringNetworkFilterSet
    table = tables.PeeringNetworkTable
    form = forms.PeeringNetworkBulkEditForm


@register_model_view(PeeringNetwork, "delete")
class PeeringNetworkDeleteView(generic.ObjectDeleteView):
    queryset = PeeringNetwork.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peeringnetwork_list"


@register_model_view(PeeringNetwork, "bulk_import", path="import", detail=False)
class PeeringNetworkBulkImportView(generic.BulkImportView):
    queryset = PeeringNetwork.objects.all()
    model_form = forms.PeeringNetworkImportForm


# =============================================================================
# PeeringConnection Views
# =============================================================================


@register_model_view(PeeringConnection, "list", path="", detail=False)
class PeeringConnectionListView(generic.ObjectListView):
    queryset = PeeringConnection.objects.all()
    filterset = filtersets.PeeringConnectionFilterSet
    filterset_form = forms.PeeringConnectionFilterForm
    table = tables.PeeringConnectionTable


@register_model_view(PeeringConnection)
class PeeringConnectionView(generic.ObjectView):
    queryset = PeeringConnection.objects.all()


@register_model_view(PeeringConnection, "add", detail=False)
@register_model_view(PeeringConnection, "edit")
class PeeringConnectionEditView(generic.ObjectEditView):
    queryset = PeeringConnection.objects.all()
    form = forms.PeeringConnectionForm


@register_model_view(PeeringConnection, "bulk_delete", path="delete", detail=False)
class PeeringConnectionBulkDeleteView(generic.BulkDeleteView):
    queryset = PeeringConnection.objects.all()
    table = tables.PeeringConnectionTable


@register_model_view(PeeringConnection, "bulk_edit", path="edit", detail=False)
class PeeringConnectionBulkEditView(generic.BulkEditView):
    queryset = PeeringConnection.objects.all()
    filterset = filtersets.PeeringConnectionFilterSet
    table = tables.PeeringConnectionTable
    form = forms.PeeringConnectionBulkEditForm


@register_model_view(PeeringConnection, "delete")
class PeeringConnectionDeleteView(generic.ObjectDeleteView):
    queryset = PeeringConnection.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peeringconnection_list"


@register_model_view(PeeringConnection, "bulk_import", path="import", detail=False)
class PeeringConnectionBulkImportView(generic.BulkImportView):
    queryset = PeeringConnection.objects.all()
    model_form = forms.PeeringConnectionImportForm


# =============================================================================
# PeeringDB Integration Views
# =============================================================================


class PeeringDBIXSearchView(View):
    """AJAX endpoint for searching PeeringDB IXes."""

    def get(self, request):
        query = request.GET.get("q", "")
        if len(query) < 2:
            return JsonResponse({"results": []})

        client = PeeringDBClient()
        try:
            results = client.search_ix(query)
            formatted = [
                {
                    "id": ix["id"],
                    "text": f"{ix['name']} ({ix.get('city', 'Unknown')}, {ix.get('country', 'XX')})",
                    "name": ix["name"],
                    "city": ix.get("city", ""),
                    "country": ix.get("country", ""),
                }
                for ix in results[:20]
            ]
            return JsonResponse({"results": formatted})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class PeeringFabricCreateFromPeeringDBView(View):
    """Create new PeeringFabric from PeeringDB IX."""

    def get(self, request):
        return render(
            request,
            "netbox_peering_manager/peeringfabric_create_from_peeringdb.html",
            {},
        )

    def post(self, request):
        ix_id = request.POST.get("ix_id")
        if not ix_id:
            messages.error(request, "Please select an IX from PeeringDB")
            return redirect("plugins:netbox_peering_manager:peeringfabric_create_from_peeringdb")

        try:
            ix_id = int(ix_id)
            client = PeeringDBClient()
            ix_data = client.get_ix(ix_id)

            name = ix_data.get("name", f"IX {ix_id}")
            fabric = PeeringFabric.objects.create(
                name=name,
                slug=slugify(name)[:100],
                description=f"Imported from PeeringDB (IX ID: {ix_id})",
            )

            link_fabric_to_peeringdb(fabric, ix_id, sync=True)

            messages.success(request, f"Created and synced fabric: {fabric}")
            return redirect(fabric.get_absolute_url())

        except Exception as e:
            messages.error(request, f"Error creating fabric: {e}")
            return redirect("plugins:netbox_peering_manager:peeringfabric_create_from_peeringdb")


@register_model_view(PeeringFabric, "sync_peeringdb")
class PeeringFabricSyncPeeringDBView(View):
    """Trigger PeeringDB sync for a fabric."""

    def post(self, request, pk):
        fabric = get_object_or_404(PeeringFabric, pk=pk)

        if not hasattr(fabric, "peeringdb") or not fabric.peeringdb:
            messages.error(request, "Fabric has no PeeringDB link")
            return redirect(fabric.get_absolute_url())

        service = PeeringDBSyncService()
        result = service.sync_fabric(fabric)

        if result.success:
            messages.success(
                request,
                f"Synced: {result.networks_created} networks created, "
                f"{result.networks_updated} updated, {result.peers_synced} peers",
            )
        else:
            messages.error(request, f"Sync errors: {', '.join(result.errors)}")

        return redirect(fabric.get_absolute_url())


@register_model_view(PeeringFabric, "create_session_from_peer")
class CreateSessionFromPeerView(View):
    """Redirect to BGPSession form with pre-filled peer data."""

    def get(self, _request, pk, peer_pk):
        fabric = get_object_or_404(PeeringFabric, pk=pk)
        peer = get_object_or_404(PeeringDBPeer, pk=peer_pk, fabric=fabric)

        params = {
            "name": peer.name,
            "remote_as": peer.asn,
        }
        if peer.ipv4_addr:
            params["remote_address"] = peer.ipv4_addr
        elif peer.ipv6_addr:
            params["remote_address"] = peer.ipv6_addr

        url = reverse("plugins:netbox_peering_manager:bgpsession_add")
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return redirect(f"{url}?{query_string}")
