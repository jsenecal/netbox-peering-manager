"""
Background jobs for IRR prefix list synchronization.
"""

import logging

from core.choices import JobStatusChoices
from django.db import transaction
from netbox.jobs import JobRunner

from netbox_peering_manager.irr_client import IRRClient, IRRClientError
from netbox_peering_manager.models import IRRPrefixListConfig

logger = logging.getLogger(__name__)

# Map netbox-routing PrefixList.family integer choices to IRR client string values
FAMILY_MAP = {4: "ipv4", 6: "ipv6"}


def _build_entries(prefix_list, prefixes):
    """Build PrefixListEntry objects linked to CustomPrefix instances."""
    from django.contrib.contenttypes.models import ContentType
    from netbox_routing.models import CustomPrefix, PrefixListEntry

    ct = ContentType.objects.get_for_model(CustomPrefix)
    custom_prefixes = CustomPrefix.objects.bulk_create([CustomPrefix(prefix=pfx) for pfx in prefixes])
    return [
        PrefixListEntry(
            prefix_list=prefix_list,
            sequence=idx + 1,
            action="permit",
            assigned_prefix_type=ct,
            assigned_prefix_id=cp.pk,
        )
        for idx, cp in enumerate(custom_prefixes)
    ]


class SyncPrefixListJob(JobRunner):
    """Sync a single PrefixList from IRR via its IRRPrefixListConfig."""

    class Meta:
        name = "Sync Prefix List from IRR"

    def run(self, *_args, **_kwargs):
        config = self.job.object

        if not config.is_irr_managed:
            self.job.data = {"error": "IRRPrefixListConfig is not IRR-managed"}
            self.job.status = JobStatusChoices.STATUS_ERRORED
            return

        irr_source = config.irr_source
        as_set = config.source_as_set
        prefix_list = config.prefix_list
        family = FAMILY_MAP.get(prefix_list.family, "both")

        self.job.data = {
            "as_set": as_set,
            "irr_source": irr_source.name,
            "prefix_list": prefix_list.name,
            "family": family,
        }

        try:
            from netbox_routing.models import PrefixListEntry

            client = IRRClient(irr_source)
            prefixes = client.fetch_prefixes(as_set, family)

            # Atomically replace entries to avoid partial state on failure
            with transaction.atomic():
                deleted_count = prefix_list.prefix_list_entries.count()
                prefix_list.prefix_list_entries.all().delete()

                entries = _build_entries(prefix_list, prefixes)
                PrefixListEntry.objects.bulk_create(entries)

            self.job.data.update(
                {
                    "deleted_entries": deleted_count,
                    "created_entries": len(entries),
                    "prefixes": len(prefixes),
                }
            )

            logger.info(
                f"Synced {len(prefixes)} prefixes for {prefix_list.name} "
                f"from {as_set} ({deleted_count} deleted, {len(entries)} created)"
            )

        except IRRClientError as e:
            self.job.data["error"] = str(e)
            self.job.status = JobStatusChoices.STATUS_ERRORED
            logger.error(f"IRR sync failed for {prefix_list.name}: {e}")
            raise

        except Exception as e:
            self.job.data["error"] = str(e)
            self.job.status = JobStatusChoices.STATUS_ERRORED
            logger.exception(f"Unexpected error syncing {prefix_list.name}")
            raise


class SyncAllPrefixListsJob(JobRunner):
    """Sync all IRR-managed PrefixLists for an IRRSource."""

    class Meta:
        name = "Sync All Prefix Lists from IRR"

    def run(self, *_args, **_kwargs):
        irr_source = self.job.object

        if not irr_source.enabled:
            self.job.data = {"error": "IRR source is disabled"}
            self.job.status = JobStatusChoices.STATUS_ERRORED
            return

        # Filter matches is_irr_managed: irr_source is non-null (matched
        # by specific object) and source_as_set is non-empty.
        configs = (
            IRRPrefixListConfig.objects.filter(
                irr_source=irr_source,
                source_as_set__isnull=False,
            )
            .exclude(source_as_set="")
            .select_related("prefix_list")
        )

        self.job.data = {
            "irr_source": irr_source.name,
            "total_configs": configs.count(),
            "synced": 0,
            "failed": 0,
            "errors": [],
        }

        client = IRRClient(irr_source)

        for config in configs:
            prefix_list = config.prefix_list
            try:
                from netbox_routing.models import PrefixListEntry

                family = FAMILY_MAP.get(prefix_list.family, "both")
                prefixes = client.fetch_prefixes(
                    config.source_as_set,
                    family,
                )

                with transaction.atomic():
                    prefix_list.prefix_list_entries.all().delete()

                    entries = _build_entries(prefix_list, prefixes)
                    PrefixListEntry.objects.bulk_create(entries)

                self.job.data["synced"] += 1

                logger.info(f"Synced {len(prefixes)} prefixes for {prefix_list.name}")

            except Exception as e:
                self.job.data["failed"] += 1
                self.job.data["errors"].append(
                    {
                        "prefix_list": prefix_list.name,
                        "error": str(e),
                    }
                )
                logger.error(f"Failed to sync {prefix_list.name}: {e}")

        if self.job.data["failed"] > 0:
            self.job.status = JobStatusChoices.STATUS_ERRORED
