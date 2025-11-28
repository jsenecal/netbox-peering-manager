from dcim.models import Site
from netbox_initializers.initializers.base import BaseInitializer, register_initializer
from tenancy.models import Tenant

from netbox_peering_manager.models import Community

MATCH_PARAMS = ["value"]
OPTIONAL_ASSOCS = {
    "site": (Site, "name"),
    "tenant": (Tenant, "name"),
}


class CommunityInitializer(BaseInitializer):
    data_file_name = "peering_manager_communities.yml"

    def load_data(self):
        data = self.load_yaml()
        if data is None:
            return

        for params in data:
            tags = params.pop("tags", None)
            custom_field_data = self.pop_custom_fields(params)

            for assoc, details in OPTIONAL_ASSOCS.items():
                if assoc in params:
                    model, field = details
                    query = {field: params.pop(assoc)}
                    params[assoc] = model.objects.get(**query)

            matching_params, defaults = self.split_params(params, MATCH_PARAMS)
            obj, created = Community.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print(f"🏷️  Created Community: {obj.value}")

            self.set_custom_fields_values(obj, custom_field_data)
            self.set_tags(obj, tags)


register_initializer("peering_manager_communities", CommunityInitializer)
