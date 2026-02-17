"""Configuration renderer service for building BGP template context."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dcim.models import Device, Platform, Site

from netbox_peering_manager.models import PeeringNetwork, PeeringSession

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from netbox_routing.models import BFDProfile, BGPPeer, BGPPeerTemplate


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
        sessions: list[PeeringSession] | None = None,
    ) -> dict[str, Any]:
        """
        Build template context for BGP configuration rendering.

        Args:
            device: Device to get all sessions for (if sessions not provided).
            sessions: Specific PeeringSession instances to include.

        Returns:
            Dict with keys: device, sessions, peer_groups, route_maps,
            prefix_lists, communities.

        Note:
            If sessions is provided, those sessions are used.
            If only device is provided, all PeeringSessions for BGPPeers
            on that device (via BGPRouter->BGPScope->BGPPeer) are fetched.
            If neither is provided, returns empty context.
        """
        if sessions is not None:
            session_queryset = self._optimize_session_queryset(
                PeeringSession.objects.filter(pk__in=[s.pk for s in sessions])
            )
        elif device is not None:
            # Find PeeringSessions via BGPRouter -> BGPScope -> BGPPeer chain
            from netbox_routing.models import BGPRouter

            router_ids = BGPRouter.objects.filter(
                assigned_object_type__model="device",
                assigned_object_id=device.pk,
            ).values_list("pk", flat=True)

            session_queryset = self._optimize_session_queryset(
                PeeringSession.objects.filter(bgp_peer__scope__router__pk__in=router_ids)
            )
        else:
            session_queryset = PeeringSession.objects.none()

        sessions_list = list(session_queryset)

        context = {
            "device": self._serialize_device(device),
            "sessions": [self._serialize_session(s) for s in sessions_list],
            "peer_groups": self._extract_peer_groups(sessions_list),
            "route_maps": self._extract_route_maps(sessions_list),
            "prefix_lists": [],
            "communities": [],
        }

        return context

    def _optimize_session_queryset(self, queryset: QuerySet[PeeringSession]) -> QuerySet[PeeringSession]:
        """Apply select_related and prefetch_related for efficient session loading."""
        return queryset.select_related(
            "bgp_peer",
            "bgp_peer__peer",  # remote IP
            "bgp_peer__source",  # local IP
            "bgp_peer__local_as",
            "bgp_peer__remote_as",
            "bgp_peer__peer_group",
            "bgp_peer__bfd",
            "bgp_peer__scope",
            "bgp_peer__scope__router",
            "relationship",
            "peering_network",
            "peering_network__fabric",
        ).prefetch_related(
            "bgp_peer__address_families",
            "bgp_peer__address_families__routemap_in",
            "bgp_peer__address_families__routemap_out",
            "bgp_peer__address_families__prefixlist_in",
            "bgp_peer__address_families__prefixlist_out",
        )

    def _serialize_device(self, device: Device | None) -> dict[str, Any] | None:
        if device is None:
            return None

        return {
            "id": device.pk,
            "name": device.name,
            "platform": self._serialize_platform(device.platform) if device.platform else None,
            "site": self._serialize_site(device.site) if device.site else None,
        }

    def _serialize_platform(self, platform: Platform) -> dict[str, Any]:
        return {
            "name": platform.name,
            "slug": platform.slug,
        }

    def _serialize_site(self, site: Site) -> dict[str, Any]:
        return {
            "name": site.name,
            "slug": site.slug,
        }

    def _serialize_session(self, session: PeeringSession) -> dict[str, Any]:
        """Serialize PeeringSession + its underlying BGPPeer to context dict."""
        peer = session.bgp_peer

        # Try to find PeerASN via the remote ASN
        peer_asn_info = self._get_peer_asn_info(peer)

        # Get address family config
        address_families = self._serialize_address_families(peer)

        return {
            "id": session.pk,
            "name": peer.name,
            "description": getattr(peer, "description", ""),
            "status": peer.status,
            "enabled": peer.enabled,
            "local_asn": peer.local_as.asn if peer.local_as else None,
            "peer_asn": peer.remote_as.asn if peer.remote_as else None,
            "peer_name": peer_asn_info.get("name"),
            "irr_as_set": peer_asn_info.get("irr_as_set"),
            "ipv4_max_prefixes": peer_asn_info.get("ipv4_max_prefixes"),
            "ipv6_max_prefixes": peer_asn_info.get("ipv6_max_prefixes"),
            "local_ip": str(peer.source.address.ip) if peer.source else None,
            "remote_ip": str(peer.peer.address.ip) if peer.peer else None,
            "relationship": session.relationship.name if session.relationship else None,
            "service_reference": session.service_reference,
            "password": peer.password or "",
            "ttl": peer.ttl,
            "bfd_profile": self._serialize_bfd(peer.bfd) if peer.bfd else None,
            "peer_group": self._serialize_peer_group(peer.peer_group) if peer.peer_group else None,
            "peering_network": self._serialize_peering_network(session.peering_network)
            if session.peering_network
            else None,
            "address_families": address_families,
            "afi_safis": self._derive_afi_safis(peer),
        }

    def _get_peer_asn_info(self, peer: BGPPeer) -> dict[str, Any]:
        """Look up PeerASN metadata for a BGPPeer's remote_as."""
        if not peer.remote_as:
            return {}

        try:
            from netbox_peering_manager.models import PeerASN

            peer_asn = PeerASN.objects.select_related("asn").get(asn=peer.remote_as)
            return {
                "name": peer_asn.name,
                "irr_as_set": peer_asn.irr_as_set,
                "ipv4_max_prefixes": peer_asn.ipv4_max_prefixes,
                "ipv6_max_prefixes": peer_asn.ipv6_max_prefixes,
            }
        except PeerASN.DoesNotExist:
            return {"name": peer.remote_as.description or f"AS{peer.remote_as.asn}"}

    def _serialize_bfd(self, bfd: BFDProfile) -> dict[str, Any]:
        return {
            "name": bfd.name,
            "minimum_interval": bfd.min_tx_int,
            "minimum_rx_interval": bfd.min_rx_int,
            "multiplier": bfd.multiplier,
            "hold": bfd.hold,
        }

    def _serialize_peer_group(self, peer_group: BGPPeerTemplate) -> dict[str, Any]:
        return {
            "id": peer_group.pk,
            "name": peer_group.name,
        }

    def _serialize_peering_network(self, peering_network: PeeringNetwork) -> dict[str, Any]:
        return {
            "id": peering_network.pk,
            "name": peering_network.name,
            "fabric": peering_network.fabric.name if peering_network.fabric else None,
        }

    def _serialize_address_families(self, peer: BGPPeer) -> list[dict[str, Any]]:
        """Serialize BGPPeerAddressFamily entries for a peer."""
        result = []
        for af in peer.address_families.all():
            entry: dict[str, Any] = {
                "afi": str(af.address_family) if af.address_family else None,
            }
            if af.routemap_in:
                entry["route_map_in"] = {"name": af.routemap_in.name}
            if af.routemap_out:
                entry["route_map_out"] = {"name": af.routemap_out.name}
            if af.prefixlist_in:
                entry["prefix_list_in"] = {"name": af.prefixlist_in.name}
            if af.prefixlist_out:
                entry["prefix_list_out"] = {"name": af.prefixlist_out.name}
            result.append(entry)
        return result

    def _derive_afi_safis(self, peer: BGPPeer) -> list[str]:
        """Derive AFI-SAFI list from peer IP address families."""
        afi_safis = []

        if peer.source:
            ip_version = peer.source.address.version
            if ip_version == 4:
                afi_safis.append("ipv4-unicast")
            elif ip_version == 6:
                afi_safis.append("ipv6-unicast")

        return afi_safis

    def _extract_peer_groups(self, sessions: list[PeeringSession]) -> list[dict[str, Any]]:
        """Extract deduplicated peer groups from sessions."""
        seen_ids: set[int] = set()
        peer_groups: list[dict[str, Any]] = []

        for session in sessions:
            pg = session.bgp_peer.peer_group
            if pg and pg.pk not in seen_ids:
                seen_ids.add(pg.pk)
                peer_groups.append(self._serialize_peer_group(pg))

        return peer_groups

    def _extract_route_maps(self, sessions: list[PeeringSession]) -> list[dict[str, Any]]:
        """Extract deduplicated route maps from sessions' address families."""
        seen_ids: set[int] = set()
        route_maps: list[dict[str, Any]] = []

        for session in sessions:
            for af in session.bgp_peer.address_families.all():
                for rm in [af.routemap_in, af.routemap_out]:
                    if rm and rm.pk not in seen_ids:
                        seen_ids.add(rm.pk)
                        route_maps.append({"id": rm.pk, "name": rm.name})

        return route_maps
