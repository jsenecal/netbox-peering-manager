from netbox_initializers.initializers.base import BaseInitializer, register_initializer

from netbox_peering_manager.models import BGPPeerGroup, RoutingPolicy

MATCH_PARAMS = ["name"]


class BGPPeerGroupInitializer(BaseInitializer):
    data_file_name = "peering_manager_peer_groups.yml"

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

            matching_params, defaults = self.split_params(params, MATCH_PARAMS)
            obj, created = BGPPeerGroup.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print(f"👥 Created Peer Group: {obj.name}")

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


register_initializer("peering_manager_peer_groups", BGPPeerGroupInitializer)
