"""PeeringDB sync service for synchronizing IX data with PeeringFabric."""

import logging
from dataclasses import dataclass, field

from django.db import IntegrityError, transaction
from django.utils import timezone
from ipam.models import Prefix

from netbox_peering_manager.models import (
    PeerASN,
    PeeringDBPeer,
    PeeringFabric,
    PeeringFabricPeeringDB,
    PeeringNetwork,
    PeeringNetworkPeeringDB,
)

from .exceptions import PeeringDBError, PeeringDBNotFoundError
from .peeringdb import PeeringDBClient, get_plugin_config

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Track outcomes of a PeeringDB sync operation."""

    fabric: PeeringFabric
    fabric_updated: bool = False
    networks_created: int = 0
    networks_updated: int = 0
    peers_synced: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if sync completed without errors."""
        return len(self.errors) == 0


class PeeringDBSyncService:
    """Service for syncing PeeringDB data to PeeringFabric models."""

    def __init__(self, client: PeeringDBClient | None = None):
        """Initialize sync service with optional PeeringDB client."""
        self.client = client or PeeringDBClient()

    def sync_fabric(self, fabric: PeeringFabric, peers_only: bool = False) -> SyncResult:
        """
        Sync PeeringDB data for a fabric.

        This is the main sync method that orchestrates syncing IX details,
        IXLANs (as PeeringNetworks), and peers.

        Args:
            fabric: The PeeringFabric to sync.
            peers_only: If True, only refresh peer cache without network changes.

        Returns:
            SyncResult with sync outcomes and any errors.
        """
        result = SyncResult(fabric=fabric)

        # Check fabric has PeeringDB link
        if not hasattr(fabric, "peeringdb") or fabric.peeringdb is None:
            result.errors.append("Fabric is not linked to PeeringDB")
            return result

        ix_id = fabric.peeringdb.ix_id
        mode = "peers only" if peers_only else "full"
        logger.info(f"Starting PeeringDB sync for fabric {fabric.name} (IX ID: {ix_id}, mode: {mode})")

        try:
            with transaction.atomic():
                if not peers_only:
                    # Sync IX details
                    self._sync_ix_details(fabric, ix_id, result)

                    # Sync IXLANs to PeeringNetworks
                    self._sync_ixlans(fabric, ix_id, result)

                # Sync peers (always)
                self._sync_peers(fabric, ix_id, result)

        except PeeringDBError as e:
            error_msg = f"PeeringDB API error during sync: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        except IntegrityError as e:
            error_msg = f"Database integrity error during sync: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        if result.success:
            logger.info(
                f"Sync completed for {fabric.name}: "
                f"networks created={result.networks_created}, "
                f"networks updated={result.networks_updated}, "
                f"peers synced={result.peers_synced}"
            )
        else:
            logger.warning(f"Sync completed with errors for {fabric.name}: {result.errors}")

        return result

    def sync_peer_asn(self, peer_asn: PeerASN) -> bool:
        """
        Sync PeerASN data from PeeringDB.

        Fetches network info from PeeringDB by ASN and updates
        the PeerASN record with prefix limits, IRR AS-SET, etc.

        Args:
            peer_asn: The PeerASN to sync.

        Returns:
            True if sync successful, False otherwise.
        """
        try:
            network = self.client.get_network(peer_asn.asn.asn)

            peer_asn.peeringdb_id = network["id"]
            peer_asn.ipv4_max_prefixes = network.get("info_prefixes4")
            peer_asn.ipv6_max_prefixes = network.get("info_prefixes6")
            peer_asn.irr_as_set = network.get("irr_as_set", "") or ""
            peer_asn.peeringdb_last_sync = timezone.now()
            peer_asn.save()

            logger.info(f"Synced PeerASN {peer_asn} from PeeringDB (network ID: {network['id']})")
            return True

        except PeeringDBNotFoundError:
            logger.warning(f"No PeeringDB network found for AS{peer_asn.asn.asn}")
            return False
        except PeeringDBError as e:
            logger.error(f"PeeringDB API error syncing PeerASN {peer_asn}: {e}")
            return False
        except IntegrityError as e:
            logger.error(f"Database error syncing PeerASN {peer_asn}: {e}")
            return False

    def _sync_ix_details(self, fabric: PeeringFabric, ix_id: int, result: SyncResult) -> None:
        """
        Sync IX details from PeeringDB to PeeringFabricPeeringDB.

        Args:
            fabric: The PeeringFabric being synced.
            ix_id: The PeeringDB IX ID.
            result: SyncResult to update.
        """
        try:
            ix_data = self.client.get_ix(ix_id)
            pdb_info = fabric.peeringdb

            # Update IX metadata
            pdb_info.name = ix_data.get("name", "")[:200]
            pdb_info.city = ix_data.get("city", "")[:100]
            pdb_info.country = ix_data.get("country", "")[:2]
            pdb_info.website = ix_data.get("website", "")[:200] if ix_data.get("website") else ""
            pdb_info.tech_email = ix_data.get("tech_email", "")[:254] if ix_data.get("tech_email") else ""
            pdb_info.last_sync = timezone.now()
            pdb_info.save()

            result.fabric_updated = True
            logger.debug(f"Updated IX details for {fabric.name}: {pdb_info.name}")

        except PeeringDBError as e:
            error_msg = f"PeeringDB API error syncing IX details: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        except IntegrityError as e:
            error_msg = f"Database error syncing IX details: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

    def _sync_ixlans(self, fabric: PeeringFabric, ix_id: int, result: SyncResult) -> None:
        """
        Sync IXLANs from PeeringDB to PeeringNetworks.

        Args:
            fabric: The PeeringFabric being synced.
            ix_id: The PeeringDB IX ID.
            result: SyncResult to update.
        """
        try:
            ixlans = self.client.get_ixlans(ix_id)
            logger.debug(f"Found {len(ixlans)} IXLANs for IX {ix_id}")

            for ixlan in ixlans:
                ixlan_id = ixlan.get("id")
                if not ixlan_id:
                    continue

                # Try to match to existing network
                network = self._match_existing_network(fabric, ixlan_id)

                if network:
                    # Update existing network's PeeringDB info
                    self._update_network_peeringdb(network, ixlan, result)
                else:
                    # Try to create new network from IXLAN
                    self._create_network_from_ixlan(fabric, ixlan, result)

        except PeeringDBError as e:
            error_msg = f"PeeringDB API error syncing IXLANs: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

    def _match_existing_network(self, fabric: PeeringFabric, ixlan_id: int) -> PeeringNetwork | None:
        """
        Match an IXLAN to an existing PeeringNetwork.

        First tries to find a network already linked to this IXLAN ID,
        then falls back to matching by prefix.

        Args:
            fabric: The PeeringFabric to search in.
            ixlan_id: The PeeringDB IXLAN ID to match.

        Returns:
            Matching PeeringNetwork or None.
        """
        # First check if already linked by IXLAN ID
        try:
            pdb_network = PeeringNetworkPeeringDB.objects.get(ixlan_id=ixlan_id)
            if pdb_network.network.fabric_id == fabric.id:
                return pdb_network.network
        except PeeringNetworkPeeringDB.DoesNotExist:
            pass

        return None

    def _update_network_peeringdb(self, network: PeeringNetwork, ixlan: dict, result: SyncResult) -> None:
        """
        Update PeeringDB info for an existing network.

        Args:
            network: The PeeringNetwork to update.
            ixlan: IXLAN data from PeeringDB.
            result: SyncResult to update.
        """
        try:
            pdb_info, created = PeeringNetworkPeeringDB.objects.get_or_create(
                network=network,
                defaults={"ixlan_id": ixlan.get("id")},
            )

            pdb_info.ixlan_id = ixlan.get("id")
            pdb_info.name = ixlan.get("name", "")[:200]
            pdb_info.mtu = ixlan.get("mtu")
            pdb_info.rs_asn = ixlan.get("rs_asn")
            pdb_info.dot1q_support = ixlan.get("dot1q_support", False)
            pdb_info.last_sync = timezone.now()
            pdb_info.save()

            result.networks_updated += 1
            logger.debug(f"Updated PeeringDB info for network {network.name}")

        except IntegrityError as e:
            error_msg = f"Database error updating network {network.name}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

    def _create_network_from_ixlan(
        self, fabric: PeeringFabric, ixlan: dict, result: SyncResult
    ) -> PeeringNetwork | None:
        """
        Create a new PeeringNetwork from IXLAN data.

        Fetches IXLAN prefixes and creates a PeeringNetwork for each,
        or creates a single network if no prefix can be matched.

        Args:
            fabric: The PeeringFabric to create the network in.
            ixlan: IXLAN data from PeeringDB.
            result: SyncResult to update.

        Returns:
            Created PeeringNetwork or None if creation failed.
        """
        ixlan_id = ixlan.get("id")
        ixlan_name = ixlan.get("name", "") or f"IXLAN-{ixlan_id}"

        try:
            # Get IXLAN prefixes
            ixpfxs = self.client.get_ixlan_prefixes(ixlan_id)
            logger.debug(f"Found {len(ixpfxs)} prefixes for IXLAN {ixlan_id}")

            if not ixpfxs:
                logger.warning(f"No prefixes found for IXLAN {ixlan_id}, skipping network creation")
                return None

            # Try to find or create NetBox Prefix for each IXLAN prefix
            for ixpfx in ixpfxs:
                prefix_str = ixpfx.get("prefix")
                if not prefix_str:
                    continue

                # Try to find existing prefix in NetBox
                try:
                    prefix = Prefix.objects.get(prefix=prefix_str)
                except Prefix.DoesNotExist:
                    # Create prefix if it doesn't exist
                    prefix = Prefix.objects.create(
                        prefix=prefix_str,
                        description=f"PeeringDB: {fabric.name} - {ixlan_name}",
                    )
                    logger.info(f"Created prefix {prefix_str} for IXLAN {ixlan_id}")

                # Check if network with this prefix already exists for this fabric
                existing = PeeringNetwork.objects.filter(fabric=fabric, prefix=prefix).first()
                if existing:
                    # Link existing network to this IXLAN
                    self._update_network_peeringdb(existing, ixlan, result)
                    continue

                # Create new PeeringNetwork
                network_name = ixlan_name[:100]
                # Make name unique if needed
                counter = 1
                base_name = network_name
                while PeeringNetwork.objects.filter(fabric=fabric, name=network_name).exists():
                    network_name = f"{base_name[:95]}-{counter}"
                    counter += 1

                network = PeeringNetwork.objects.create(
                    fabric=fabric,
                    name=network_name,
                    prefix=prefix,
                    description=f"Auto-created from PeeringDB IXLAN {ixlan_id}",
                )

                # Create PeeringDB info for the network
                PeeringNetworkPeeringDB.objects.create(
                    network=network,
                    ixlan_id=ixlan_id,
                    name=ixlan.get("name", "")[:200],
                    mtu=ixlan.get("mtu"),
                    rs_asn=ixlan.get("rs_asn"),
                    dot1q_support=ixlan.get("dot1q_support", False),
                )

                result.networks_created += 1
                logger.info(f"Created network {network.name} for IXLAN {ixlan_id}")

            return None  # Multiple networks may have been created

        except PeeringDBError as e:
            error_msg = f"PeeringDB API error creating network from IXLAN {ixlan_id}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            return None
        except IntegrityError as e:
            error_msg = f"Database error creating network from IXLAN {ixlan_id}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            return None

    def _sync_peers(self, fabric: PeeringFabric, ix_id: int, result: SyncResult) -> None:
        """
        Sync peer data from PeeringDB.

        Clears existing PeeringDBPeer records for the fabric and creates
        new ones from netixlan data.

        Args:
            fabric: The PeeringFabric being synced.
            ix_id: The PeeringDB IX ID.
            result: SyncResult to update.
        """
        try:
            # Get local ASNs to filter out
            local_asns = get_plugin_config("local_asns", [])
            if not isinstance(local_asns, list):
                local_asns = [local_asns] if local_asns else []
            local_asns = set(local_asns)

            # Get all IXLANs for this IX
            ixlans = self.client.get_ixlans(ix_id)

            # Clear existing peers for this fabric
            deleted_count = PeeringDBPeer.objects.filter(fabric=fabric).delete()[0]
            logger.debug(f"Cleared {deleted_count} existing peers for {fabric.name}")

            peers_created = 0
            for ixlan in ixlans:
                ixlan_id = ixlan.get("id")
                if not ixlan_id:
                    continue

                # Get network connections (netixlans) for this IXLAN
                netixlans = self.client.get_netixlans(ixlan_id)
                logger.debug(f"Found {len(netixlans)} network connections for IXLAN {ixlan_id}")

                for netixlan in netixlans:
                    asn = netixlan.get("asn")
                    if not asn:
                        continue

                    # Skip local ASNs
                    if asn in local_asns:
                        logger.debug(f"Skipping local ASN {asn}")
                        continue

                    # Get IP addresses
                    ipv4_addr = netixlan.get("ipaddr4")
                    ipv6_addr = netixlan.get("ipaddr6")

                    # Skip if no IP addresses
                    if not ipv4_addr and not ipv6_addr:
                        continue

                    # Create peer record
                    try:
                        PeeringDBPeer.objects.create(
                            fabric=fabric,
                            asn=asn,
                            name=netixlan.get("name", "")[:200] or f"AS{asn}",
                            ipv4_addr=ipv4_addr,
                            ipv6_addr=ipv6_addr,
                            is_rs_peer=netixlan.get("is_rs_peer", False),
                            speed=netixlan.get("speed", 0) or 0,
                        )
                        peers_created += 1
                    except IntegrityError as e:
                        # Log but continue - duplicates may occur
                        logger.debug(f"Could not create peer AS{asn} (duplicate?): {e}")

            result.peers_synced = peers_created
            logger.info(f"Synced {peers_created} peers for {fabric.name}")

        except PeeringDBError as e:
            error_msg = f"PeeringDB API error syncing peers: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        except IntegrityError as e:
            error_msg = f"Database error syncing peers: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)


def link_fabric_to_peeringdb(
    fabric: PeeringFabric,
    ix_id: int,
    sync: bool = True,
) -> SyncResult | PeeringFabricPeeringDB:
    """
    Link a PeeringFabric to a PeeringDB IX and optionally sync.

    Args:
        fabric: The PeeringFabric to link.
        ix_id: The PeeringDB IX ID to link to.
        sync: If True, sync data after linking. Default True.

    Returns:
        SyncResult if sync=True, otherwise PeeringFabricPeeringDB.
    """
    logger.info(f"Linking fabric {fabric.name} to PeeringDB IX {ix_id}")

    # Create or update the PeeringDB link
    pdb_info, created = PeeringFabricPeeringDB.objects.update_or_create(
        fabric=fabric,
        defaults={"ix_id": ix_id},
    )

    if created:
        logger.info(f"Created PeeringDB link for {fabric.name} -> IX {ix_id}")
    else:
        logger.info(f"Updated PeeringDB link for {fabric.name} -> IX {ix_id}")

    if sync:
        service = PeeringDBSyncService()
        return service.sync_fabric(fabric)

    return pdb_info
