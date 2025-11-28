from dcim.models import Device, Site
from ipam.models import ASN, IPAddress
from netbox_initializers.initializers.base import BaseInitializer, register_initializer
from tenancy.models import Tenant

from netbox_peering_manager.models import (
    BFD,
    BGPPeerGroup,
    BGPSession,
    PrefixList,
    Relationship,
    RoutingPolicy,
)

MATCH_PARAMS = ["local_as", "remote_as", "local_address", "remote_address"]
REQUIRED_ASSOCS = {
    "local_as": (ASN, "asn"),
    "remote_as": (ASN, "asn"),
    "local_address": (IPAddress, "address"),
    "remote_address": (IPAddress, "address"),
}
OPTIONAL_ASSOCS = {
    "device": (Device, "name"),
    "site": (Site, "name"),
    "tenant": (Tenant, "name"),
    "relationship": (Relationship, "name"),
    "bfd": (BFD, "name"),
    "peer_group": (BGPPeerGroup, "name"),
    "prefix_list_in": (PrefixList, "name"),
    "prefix_list_out": (PrefixList, "name"),
}


class BGPSessionInitializer(BaseInitializer):
    data_file_name = "peering_manager_sessions.yml"

    def load_data(self):
        data = self.load_yaml()
        if data is None:
            return

        for params in data:
            tags = params.pop("tags", None)
            custom_field_data = self.pop_custom_fields(params)

            # Handle M2M fields separately
            import_policies = params.pop("import_policies", [])
            export_policies = params.pop("export_policies", [])

            # Resolve required associations
            for assoc, details in REQUIRED_ASSOCS.items():
                if assoc in params:
                    model, field = details
                    query = {field: params.pop(assoc)}
                    try:
                        params[assoc] = model.objects.get(**query)
                    except model.DoesNotExist:
                        print(f"⚠️  {assoc} not found: {query}")
                        break
            else:
                # Resolve optional associations
                for assoc, details in OPTIONAL_ASSOCS.items():
                    if assoc in params:
                        model, field = details
                        query = {field: params.pop(assoc)}
                        try:
                            params[assoc] = model.objects.get(**query)
                        except model.DoesNotExist:
                            print(f"⚠️  {assoc} not found: {query}")

                matching_params, defaults = self.split_params(params, MATCH_PARAMS)
                obj, created = BGPSession.objects.get_or_create(**matching_params, defaults=defaults)

                if created:
                    print(f"🔗 Created BGP Session: {obj.name}")

                # Set M2M relationships
                for policy_name in import_policies:
                    try:
                        policy = RoutingPolicy.objects.get(name=policy_name)
                        obj.import_policies.add(policy)
                    except RoutingPolicy.DoesNotExist:
                        print(f"⚠️  Import policy not found: {policy_name}")

                for policy_name in export_policies:
                    try:
                        policy = RoutingPolicy.objects.get(name=policy_name)
                        obj.export_policies.add(policy)
                    except RoutingPolicy.DoesNotExist:
                        print(f"⚠️  Export policy not found: {policy_name}")

                self.set_custom_fields_values(obj, custom_field_data)
                self.set_tags(obj, tags)


register_initializer("peering_manager_sessions", BGPSessionInitializer)
