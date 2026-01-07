"""Configuration renderer service for building BGP template context."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dcim.models import Device
from django.db.models import Prefetch

from netbox_peering_manager.models import (
    BGPPeerGroup,
    BGPSession,
    RoutingPolicy,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ConfigRenderer:
    """
    Service for building template context for BGP configuration rendering.

    Builds a denormalized context dict with all BGP objects needed for
    configuration templating, optimized with select_related and prefetch_related
    for efficient database access.
    """

    def build_context(
        self,
        device: Device | None = None,
        sessions: list[BGPSession] | None = None,
    ) -> dict[str, Any]:
        """
        Build template context for BGP configuration rendering.

        Args:
            device: Device to get all sessions for (if sessions not provided).
            sessions: Specific BGPSession instances to include.

        Returns:
            Dict with keys: device, sessions, peer_groups, routing_policies,
            prefix_lists, communities.

        Note:
            If sessions is provided, those sessions are used.
            If only device is provided, all sessions for that device are fetched.
            If neither is provided, returns empty context.
        """
        # Determine which sessions to use
        if sessions is not None:
            session_queryset = self._optimize_session_queryset(
                BGPSession.objects.filter(pk__in=[s.pk for s in sessions])
            )
        elif device is not None:
            session_queryset = self._optimize_session_queryset(BGPSession.objects.filter(device=device))
        else:
            session_queryset = BGPSession.objects.none()

        # Fetch optimized sessions
        sessions_list = list(session_queryset)

        # Build context
        context = {
            "device": self._serialize_device(device),
            "sessions": [self._serialize_session(s) for s in sessions_list],
            "peer_groups": self._extract_peer_groups(sessions_list),
            "routing_policies": self._extract_routing_policies(sessions_list),
            "prefix_lists": [],  # Placeholder for future
            "communities": [],  # Placeholder for future
        }

        return context

    def _optimize_session_queryset(self, queryset: QuerySet[BGPSession]) -> QuerySet[BGPSession]:
        """
        Apply select_related and prefetch_related for efficient session loading.

        Args:
            queryset: Base BGPSession queryset.

        Returns:
            Optimized queryset with related objects prefetched.
        """
        return queryset.select_related(
            "device",
            "device__platform",
            "device__site",
            "local_as",
            "remote_as",
            "local_address",
            "remote_address",
            "peer_group",
            "relationship",
            "bfd",
            "peering_network",
            "peering_network__fabric",
        ).prefetch_related(
            Prefetch(
                "import_policies",
                queryset=RoutingPolicy.objects.order_by("-weight", "name"),
            ),
            Prefetch(
                "export_policies",
                queryset=RoutingPolicy.objects.order_by("-weight", "name"),
            ),
        )

    def _serialize_device(self, device: Device | None) -> dict[str, Any] | None:
        """
        Serialize device to context dict.

        Args:
            device: Device instance or None.

        Returns:
            Serialized device dict or None.
        """
        if device is None:
            return None

        return {
            "id": device.pk,
            "name": device.name,
            "platform": self._serialize_platform(device.platform) if device.platform else None,
            "site": self._serialize_site(device.site) if device.site else None,
        }

    def _serialize_platform(self, platform) -> dict[str, Any]:
        """
        Serialize platform to context dict.

        Args:
            platform: Platform instance.

        Returns:
            Serialized platform dict.
        """
        return {
            "name": platform.name,
            "slug": platform.slug,
        }

    def _serialize_site(self, site) -> dict[str, Any]:
        """
        Serialize site to context dict.

        Args:
            site: Site instance.

        Returns:
            Serialized site dict.
        """
        return {
            "name": site.name,
            "slug": site.slug,
        }

    def _serialize_session(self, session: BGPSession) -> dict[str, Any]:
        """
        Serialize BGPSession to context dict.

        Args:
            session: BGPSession instance.

        Returns:
            Serialized session dict with all related data.
        """
        return {
            "id": session.pk,
            "name": session.name,
            "description": session.description,
            "status": session.status,
            "enabled": session.enabled,
            "local_asn": session.local_as.asn if session.local_as else None,
            "peer_asn": session.remote_as.asn if session.remote_as else None,
            "local_ip": str(session.local_address.address.ip) if session.local_address else None,
            "remote_ip": str(session.remote_address.address.ip) if session.remote_address else None,
            "relationship": session.relationship.name if session.relationship else None,
            "password": session.password,
            "multihop_ttl": session.multihop_ttl,
            "bfd_profile": self._serialize_bfd(session.bfd) if session.bfd else None,
            "peer_group": self._serialize_peer_group(session.peer_group) if session.peer_group else None,
            "peering_network": self._serialize_peering_network(session.peering_network)
            if session.peering_network
            else None,
            "import_policies": [self._serialize_policy(p) for p in session.import_policies.all()],
            "export_policies": [self._serialize_policy(p) for p in session.export_policies.all()],
            "afi_safis": self._derive_afi_safis(session),
        }

    def _serialize_bfd(self, bfd) -> dict[str, Any]:
        """
        Serialize BFD profile to context dict.

        Args:
            bfd: BFD instance.

        Returns:
            Serialized BFD dict.
        """
        return {
            "name": bfd.name,
            "minimum_interval": bfd.minimum_transmit_interval,
            "multiplier": bfd.detect_multiplier,
        }

    def _serialize_peer_group(self, peer_group: BGPPeerGroup) -> dict[str, Any]:
        """
        Serialize BGPPeerGroup to context dict.

        Args:
            peer_group: BGPPeerGroup instance.

        Returns:
            Serialized peer group dict.
        """
        return {
            "id": peer_group.pk,
            "name": peer_group.name,
            "slug": peer_group.name.lower().replace(" ", "-"),  # Generate slug from name
            "description": peer_group.description,
        }

    def _serialize_peering_network(self, peering_network) -> dict[str, Any]:
        """
        Serialize PeeringNetwork to context dict.

        Args:
            peering_network: PeeringNetwork instance.

        Returns:
            Serialized peering network dict.
        """
        return {
            "id": peering_network.pk,
            "name": peering_network.name,
            "fabric": peering_network.fabric.name if peering_network.fabric else None,
        }

    def _serialize_policy(self, policy: RoutingPolicy) -> dict[str, Any]:
        """
        Serialize RoutingPolicy to context dict.

        Args:
            policy: RoutingPolicy instance.

        Returns:
            Serialized policy dict.
        """
        return {
            "id": policy.pk,
            "name": policy.name,
            "slug": policy.name.lower().replace(" ", "-"),  # Generate slug from name
            "description": policy.description,
            "weight": policy.weight,
            "address_family": policy.address_family,
        }

    def _derive_afi_safis(self, session: BGPSession) -> list[str]:
        """
        Derive AFI-SAFI list from session IP address families.

        Since afi_safi is not yet implemented on BGPSession model,
        derive from the local/remote address families.

        Args:
            session: BGPSession instance.

        Returns:
            List of AFI-SAFI strings (e.g., ["ipv4-unicast"]).
        """
        afi_safis = []

        # Check local address family
        if session.local_address:
            ip_version = session.local_address.address.version
            if ip_version == 4:
                afi_safis.append("ipv4-unicast")
            elif ip_version == 6:
                afi_safis.append("ipv6-unicast")

        return afi_safis

    def _extract_peer_groups(self, sessions: list[BGPSession]) -> list[dict[str, Any]]:
        """
        Extract deduplicated peer groups from sessions.

        Args:
            sessions: List of BGPSession instances.

        Returns:
            List of serialized peer group dicts, deduplicated by ID.
        """
        seen_ids: set[int] = set()
        peer_groups: list[dict[str, Any]] = []

        for session in sessions:
            if session.peer_group and session.peer_group.pk not in seen_ids:
                seen_ids.add(session.peer_group.pk)
                peer_groups.append(self._serialize_peer_group(session.peer_group))

        return peer_groups

    def _extract_routing_policies(self, sessions: list[BGPSession]) -> list[dict[str, Any]]:
        """
        Extract deduplicated routing policies from sessions.

        Args:
            sessions: List of BGPSession instances.

        Returns:
            List of serialized policy dicts, deduplicated by ID.
        """
        seen_ids: set[int] = set()
        policies: list[dict[str, Any]] = []

        for session in sessions:
            for policy in session.import_policies.all():
                if policy.pk not in seen_ids:
                    seen_ids.add(policy.pk)
                    policies.append(self._serialize_policy(policy))

            for policy in session.export_policies.all():
                if policy.pk not in seen_ids:
                    seen_ids.add(policy.pk)
                    policies.append(self._serialize_policy(policy))

        return policies
