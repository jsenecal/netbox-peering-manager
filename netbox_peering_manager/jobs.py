"""
Background jobs for IRR prefix list synchronization.
"""

import logging

from core.choices import JobStatusChoices
from netbox.jobs import JobRunner

from netbox_peering_manager.irr_client import IRRClient, IRRClientError
from netbox_peering_manager.models import PrefixList, PrefixListRule

logger = logging.getLogger(__name__)


class SyncPrefixListJob(JobRunner):
    """Sync a single PrefixList from IRR."""

    class Meta:
        name = "Sync Prefix List from IRR"

    def run(self, *_args, **_kwargs):
        prefix_list = self.job.object

        if not prefix_list.is_irr_managed:
            self.job.data = {"error": "PrefixList is not IRR-managed"}
            self.job.status = JobStatusChoices.STATUS_ERRORED
            return

        irr_source = prefix_list.irr_source
        as_set = prefix_list.source_as_set
        family = prefix_list.family

        self.job.data = {
            "as_set": as_set,
            "irr_source": irr_source.name,
            "family": family,
        }

        try:
            client = IRRClient(irr_source)
            prefixes = client.fetch_prefixes(as_set, family)

            # Delete existing rules
            deleted_count = prefix_list.prefrules.count()
            prefix_list.prefrules.all().delete()

            # Create new rules
            rules = []
            for index, prefix in enumerate(prefixes):
                rules.append(
                    PrefixListRule(
                        prefix_list=prefix_list,
                        index=(index + 1) * 10,
                        action="permit",
                        prefix_custom=prefix,
                    )
                )

            PrefixListRule.objects.bulk_create(rules)

            self.job.data.update(
                {
                    "deleted_rules": deleted_count,
                    "created_rules": len(rules),
                    "prefixes": len(prefixes),
                }
            )

            logger.info(
                f"Synced {len(prefixes)} prefixes for {prefix_list.name} "
                f"from {as_set} ({deleted_count} deleted, {len(rules)} created)"
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

        prefix_lists = PrefixList.objects.filter(
            irr_source=irr_source,
            source_as_set__isnull=False,
        ).exclude(source_as_set="")

        self.job.data = {
            "irr_source": irr_source.name,
            "total_prefix_lists": prefix_lists.count(),
            "synced": 0,
            "failed": 0,
            "errors": [],
        }

        client = IRRClient(irr_source)

        for prefix_list in prefix_lists:
            try:
                prefixes = client.fetch_prefixes(
                    prefix_list.source_as_set,
                    prefix_list.family,
                )

                prefix_list.prefrules.all().delete()

                rules = []
                for index, prefix in enumerate(prefixes):
                    rules.append(
                        PrefixListRule(
                            prefix_list=prefix_list,
                            index=(index + 1) * 10,
                            action="permit",
                            prefix_custom=prefix,
                        )
                    )

                PrefixListRule.objects.bulk_create(rules)
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
