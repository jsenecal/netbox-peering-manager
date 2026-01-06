# ruff: noqa: F401
# Import all initializers to register them with netbox-initializers
try:
    from .bfd import BFDInitializer
    from .communities import CommunityInitializer
    from .peer_groups import BGPPeerGroupInitializer
    from .prefix_lists import PrefixListInitializer
    from .relationships import RelationshipInitializer
    from .routing_policies import RoutingPolicyInitializer
    from .sessions import BGPSessionInitializer
except (ImportError, Exception):
    # netbox-initializers not installed or database not ready
    pass
