"""Management command to sync PeeringDB data."""

from django.core.management.base import BaseCommand, CommandError

from netbox_peering_manager.models import PeeringFabric, PeeringFabricPeeringDB
from netbox_peering_manager.services import PeeringDBSyncService


class Command(BaseCommand):
    help = "Synchronize PeeringFabric data from PeeringDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fabric",
            type=int,
            help="Fabric PK to sync",
        )
        parser.add_argument(
            "--ix-id",
            type=int,
            help="PeeringDB IX ID to sync (creates link if needed)",
        )
        parser.add_argument(
            "--discover-only",
            action="store_true",
            help="Only refresh peer cache, no network changes",
        )

    def handle(self, **options):
        service = PeeringDBSyncService()

        if options["ix_id"]:
            self._sync_by_ix_id(options["ix_id"], service)
        elif options["fabric"]:
            self._sync_by_fabric_pk(options["fabric"], service)
        else:
            self._sync_all(service)

    def _sync_by_ix_id(self, ix_id: int, service: PeeringDBSyncService):
        """Sync fabric by PeeringDB IX ID."""
        try:
            pdb_info = PeeringFabricPeeringDB.objects.get(ix_id=ix_id)
            fabric = pdb_info.fabric
        except PeeringFabricPeeringDB.DoesNotExist as err:
            msg = f"No fabric linked to PeeringDB IX ID {ix_id}. Create a fabric and link it first."
            raise CommandError(msg) from err

        self._sync_fabric(fabric, service)

    def _sync_by_fabric_pk(self, pk: int, service: PeeringDBSyncService):
        """Sync specific fabric by PK."""
        try:
            fabric = PeeringFabric.objects.get(pk=pk)
        except PeeringFabric.DoesNotExist as err:
            msg = f"Fabric with PK {pk} not found"
            raise CommandError(msg) from err

        if not hasattr(fabric, "peeringdb"):
            msg = f"Fabric {fabric} has no PeeringDB link"
            raise CommandError(msg)

        self._sync_fabric(fabric, service)

    def _sync_all(self, service: PeeringDBSyncService):
        """Sync all fabrics with PeeringDB links."""
        fabrics = PeeringFabric.objects.filter(peeringdb__isnull=False)

        if not fabrics.exists():
            self.stdout.write(self.style.WARNING("No fabrics with PeeringDB links found"))
            return

        for fabric in fabrics:
            self._sync_fabric(fabric, service)

    def _sync_fabric(self, fabric: PeeringFabric, service: PeeringDBSyncService):
        """Sync a single fabric and report results."""
        self.stdout.write(f"Syncing {fabric}...")

        result = service.sync_fabric(fabric)

        if result.success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Synced: {result.networks_created} networks created, "
                    f"{result.networks_updated} updated, {result.peers_synced} peers"
                )
            )
        else:
            self.stdout.write(self.style.ERROR(f"  Errors: {', '.join(result.errors)}"))
