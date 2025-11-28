from netbox_initializers.initializers.base import BaseInitializer, register_initializer

from netbox_peering_manager.models import BFD

MATCH_PARAMS = ["name"]


class BFDInitializer(BaseInitializer):
    data_file_name = "peering_manager_bfd.yml"

    def load_data(self):
        data = self.load_yaml()
        if data is None:
            return

        for params in data:
            tags = params.pop("tags", None)
            custom_field_data = self.pop_custom_fields(params)

            matching_params, defaults = self.split_params(params, MATCH_PARAMS)
            obj, created = BFD.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print(f"📡 Created BFD Profile: {obj.name}")

            self.set_custom_fields_values(obj, custom_field_data)
            self.set_tags(obj, tags)


register_initializer("peering_manager_bfd", BFDInitializer)
