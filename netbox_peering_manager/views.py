from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View
from netbox.views import generic
from utilities.views import register_model_view

from . import filtersets, forms, tables
from .jobs import SyncPrefixListJob
from .models import (
    IRRPrefixListConfig,
    IRRSource,
    PeerASN,
    PeeringConnection,
    PeeringFabric,
    PeeringFabricType,
    PeeringNetwork,
    PeeringSession,
    Relationship,
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

    def get_extra_context(self, request, instance):
        sessions = PeeringSession.objects.filter(relationship=instance)
        sessions_table = tables.PeeringSessionTable(sessions)
        sessions_table.configure(request)
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
# Peer ASN Views
# =============================================================================


@register_model_view(PeerASN)
class PeerASNView(generic.ObjectView):
    queryset = PeerASN.objects.all()

    def get_extra_context(self, request, instance):
        sessions = PeeringSession.objects.filter(bgp_peer__remote_as=instance.asn)
        sessions_table = tables.PeeringSessionTable(sessions)
        sessions_table.configure(request)
        return {
            "sessions_table": sessions_table,
        }


@register_model_view(PeerASN, "list", path="", detail=False)
class PeerASNListView(generic.ObjectListView):
    queryset = PeerASN.objects.all()
    table = tables.PeerASNTable
    filterset = filtersets.PeerASNFilterSet
    filterset_form = forms.PeerASNFilterForm


@register_model_view(PeerASN, "add", detail=False)
@register_model_view(PeerASN, "edit")
class PeerASNEditView(generic.ObjectEditView):
    queryset = PeerASN.objects.all()
    form = forms.PeerASNForm


@register_model_view(PeerASN, "delete")
class PeerASNDeleteView(generic.ObjectDeleteView):
    queryset = PeerASN.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peerasn_list"


@register_model_view(PeerASN, "bulk_edit", path="edit", detail=False)
class PeerASNBulkEditView(generic.BulkEditView):
    queryset = PeerASN.objects.all()
    filterset = filtersets.PeerASNFilterSet
    table = tables.PeerASNTable
    form = forms.PeerASNBulkEditForm


@register_model_view(PeerASN, "bulk_delete", path="delete", detail=False)
class PeerASNBulkDeleteView(generic.BulkDeleteView):
    queryset = PeerASN.objects.all()
    filterset = filtersets.PeerASNFilterSet
    table = tables.PeerASNTable


@register_model_view(PeerASN, "bulk_import", path="import", detail=False)
class PeerASNBulkImportView(generic.BulkImportView):
    queryset = PeerASN.objects.all()
    model_form = forms.PeerASNImportForm


# =============================================================================
# IRRSource Views
# =============================================================================


@register_model_view(IRRSource, "list", path="", detail=False)
class IRRSourceListView(generic.ObjectListView):
    queryset = IRRSource.objects.annotate(prefix_list_count=Count("irr_prefix_list_configs"))
    filterset = filtersets.IRRSourceFilterSet
    filterset_form = forms.IRRSourceFilterForm
    table = tables.IRRSourceTable


@register_model_view(IRRSource)
class IRRSourceView(generic.ObjectView):
    queryset = IRRSource.objects.all()

    def get_extra_context(self, request, instance):
        configs = IRRPrefixListConfig.objects.filter(irr_source=instance)
        configs_table = tables.IRRPrefixListConfigTable(configs)
        configs_table.configure(request)
        return {"configs_table": configs_table}


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


# =============================================================================
# IRRPrefixListConfig Views
# =============================================================================


@register_model_view(IRRPrefixListConfig, "list", path="", detail=False)
class IRRPrefixListConfigListView(generic.ObjectListView):
    queryset = IRRPrefixListConfig.objects.select_related("prefix_list", "irr_source")
    filterset = filtersets.IRRPrefixListConfigFilterSet
    filterset_form = forms.IRRPrefixListConfigFilterForm
    table = tables.IRRPrefixListConfigTable


@register_model_view(IRRPrefixListConfig)
class IRRPrefixListConfigView(generic.ObjectView):
    queryset = IRRPrefixListConfig.objects.all()


@register_model_view(IRRPrefixListConfig, "add", detail=False)
@register_model_view(IRRPrefixListConfig, "edit")
class IRRPrefixListConfigEditView(generic.ObjectEditView):
    queryset = IRRPrefixListConfig.objects.all()
    form = forms.IRRPrefixListConfigForm


@register_model_view(IRRPrefixListConfig, "bulk_delete", path="delete", detail=False)
class IRRPrefixListConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = IRRPrefixListConfig.objects.all()
    table = tables.IRRPrefixListConfigTable


@register_model_view(IRRPrefixListConfig, "bulk_edit", path="edit", detail=False)
class IRRPrefixListConfigBulkEditView(generic.BulkEditView):
    queryset = IRRPrefixListConfig.objects.all()
    filterset = filtersets.IRRPrefixListConfigFilterSet
    table = tables.IRRPrefixListConfigTable
    form = forms.IRRPrefixListConfigBulkEditForm


@register_model_view(IRRPrefixListConfig, "delete")
class IRRPrefixListConfigDeleteView(generic.ObjectDeleteView):
    queryset = IRRPrefixListConfig.objects.all()
    default_return_url = "plugins:netbox_peering_manager:irrprefixlistconfig_list"


@register_model_view(IRRPrefixListConfig, "bulk_import", path="import", detail=False)
class IRRPrefixListConfigBulkImportView(generic.BulkImportView):
    queryset = IRRPrefixListConfig.objects.all()
    model_form = forms.IRRPrefixListConfigImportForm


@register_model_view(IRRPrefixListConfig, "sync", path="sync")
class IRRPrefixListConfigSyncView(View):
    """Trigger IRR sync for an IRRPrefixListConfig."""

    def post(self, request, pk):
        config = get_object_or_404(IRRPrefixListConfig, pk=pk)

        if not config.is_irr_managed:
            messages.error(request, "This prefix list config is not IRR-managed.")
            return redirect(config.get_absolute_url())

        SyncPrefixListJob.enqueue(instance=config, user=request.user)
        messages.success(request, f"Sync job enqueued for {config.prefix_list.name}")
        return redirect(config.get_absolute_url())


# =============================================================================
# PeeringSession Views
# =============================================================================


@register_model_view(PeeringSession, "list", path="", detail=False)
class PeeringSessionListView(generic.ObjectListView):
    queryset = PeeringSession.objects.select_related("bgp_peer", "relationship", "peering_network")
    filterset = filtersets.PeeringSessionFilterSet
    filterset_form = forms.PeeringSessionFilterForm
    table = tables.PeeringSessionTable


@register_model_view(PeeringSession)
class PeeringSessionView(generic.ObjectView):
    queryset = PeeringSession.objects.all()


@register_model_view(PeeringSession, "add", detail=False)
@register_model_view(PeeringSession, "edit")
class PeeringSessionEditView(generic.ObjectEditView):
    queryset = PeeringSession.objects.all()
    form = forms.PeeringSessionForm


@register_model_view(PeeringSession, "bulk_delete", path="delete", detail=False)
class PeeringSessionBulkDeleteView(generic.BulkDeleteView):
    queryset = PeeringSession.objects.all()
    table = tables.PeeringSessionTable


@register_model_view(PeeringSession, "bulk_edit", path="edit", detail=False)
class PeeringSessionBulkEditView(generic.BulkEditView):
    queryset = PeeringSession.objects.all()
    filterset = filtersets.PeeringSessionFilterSet
    table = tables.PeeringSessionTable
    form = forms.PeeringSessionBulkEditForm


@register_model_view(PeeringSession, "delete")
class PeeringSessionDeleteView(generic.ObjectDeleteView):
    queryset = PeeringSession.objects.all()
    default_return_url = "plugins:netbox_peering_manager:peeringsession_list"


@register_model_view(PeeringSession, "bulk_import", path="import", detail=False)
class PeeringSessionBulkImportView(generic.BulkImportView):
    queryset = PeeringSession.objects.all()
    model_form = forms.PeeringSessionImportForm


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

    def get_extra_context(self, request, instance):
        fabrics = PeeringFabric.objects.filter(type=instance)
        fabrics_table = tables.PeeringFabricTable(fabrics)
        fabrics_table.configure(request)
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

    def get_extra_context(self, request, instance):
        networks = PeeringNetwork.objects.filter(fabric=instance)
        networks_table = tables.PeeringNetworkTable(networks)
        networks_table.configure(request)
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

    def get_extra_context(self, request, instance):
        connections = PeeringConnection.objects.filter(peering_network=instance)
        connections_table = tables.PeeringConnectionTable(connections)
        connections_table.configure(request)
        sessions = PeeringSession.objects.filter(peering_network=instance)
        sessions_table = tables.PeeringSessionTable(sessions)
        sessions_table.configure(request)
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
