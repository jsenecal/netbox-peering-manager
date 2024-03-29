# Generated by Django 4.2.4 on 2023-09-18 15:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ipam.fields
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("ipam", "0064_clear_search_cache"),
        ("tenancy", "0009_standardize_description_comments"),
        ("extras", "0084_staging"),
        ("dcim", "0167_module_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Community",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("status", models.CharField(default="active", max_length=50)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "value",
                    models.CharField(max_length=64, validators=[django.core.validators.RegexValidator("\\d+:\\d+")]),
                ),
                (
                    "role",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ipam.role"
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="%(class)s_related",
                        to="dcim.site",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="tenancy.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Communities",
            },
        ),
        migrations.CreateModel(
            name="PrefixList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("family", models.CharField(max_length=10)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name_plural": "Prefix Lists",
                "unique_together": {("name", "description", "family")},
            },
        ),
        migrations.CreateModel(
            name="RoutingPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name_plural": "Routing Policies",
                "unique_together": {("name", "description")},
            },
        ),
        migrations.CreateModel(
            name="BGPPeerGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "export_policies",
                    models.ManyToManyField(
                        blank=True, related_name="group_export_policies", to="netbox_peering_manager.routingpolicy"
                    ),
                ),
                (
                    "import_policies",
                    models.ManyToManyField(
                        blank=True, related_name="group_import_policies", to="netbox_peering_manager.routingpolicy"
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name_plural": "Peer Groups",
                "unique_together": {("name", "description")},
            },
        ),
        migrations.CreateModel(
            name="RoutingPolicyRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("index", models.PositiveIntegerField()),
                ("action", models.CharField(max_length=30)),
                ("description", models.CharField(blank=True, max_length=500)),
                ("continue_entry", models.PositiveIntegerField(blank=True, null=True)),
                ("match_custom", models.JSONField(blank=True, null=True)),
                ("set_actions", models.JSONField(blank=True, null=True)),
                (
                    "match_community",
                    models.ManyToManyField(blank=True, related_name="+", to="netbox_peering_manager.community"),
                ),
                (
                    "match_ip_address",
                    models.ManyToManyField(blank=True, related_name="plrules", to="netbox_peering_manager.prefixlist"),
                ),
                (
                    "match_ipv6_address",
                    models.ManyToManyField(
                        blank=True, related_name="plrules6", to="netbox_peering_manager.prefixlist"
                    ),
                ),
                (
                    "routing_policy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rules",
                        to="netbox_peering_manager.routingpolicy",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ("routing_policy", "index"),
                "unique_together": {("routing_policy", "index")},
            },
        ),
        migrations.CreateModel(
            name="PrefixListRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("index", models.PositiveIntegerField()),
                ("action", models.CharField(max_length=30)),
                ("prefix_custom", ipam.fields.IPNetworkField(blank=True, null=True)),
                (
                    "ge",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(128),
                        ],
                    ),
                ),
                (
                    "le",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(128),
                        ],
                    ),
                ),
                (
                    "prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "prefix_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prefrules",
                        to="netbox_peering_manager.prefixlist",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ("prefix_list", "index"),
                "unique_together": {("prefix_list", "index")},
            },
        ),
        migrations.CreateModel(
            name="BGPSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("name", models.CharField(blank=True, max_length=64, null=True)),
                ("status", models.CharField(default="active", max_length=50)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "device",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="dcim.device"
                    ),
                ),
                (
                    "export_policies",
                    models.ManyToManyField(
                        blank=True, related_name="session_export_policies", to="netbox_peering_manager.routingpolicy"
                    ),
                ),
                (
                    "import_policies",
                    models.ManyToManyField(
                        blank=True, related_name="session_import_policies", to="netbox_peering_manager.routingpolicy"
                    ),
                ),
                (
                    "local_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="local_address", to="ipam.ipaddress"
                    ),
                ),
                (
                    "local_as",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="local_as", to="ipam.asn"
                    ),
                ),
                (
                    "peer_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="netbox_peering_manager.bgppeergroup",
                    ),
                ),
                (
                    "remote_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="remote_address", to="ipam.ipaddress"
                    ),
                ),
                (
                    "remote_as",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="remote_as", to="ipam.asn"
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="dcim.site"
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="tenancy.tenant"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "BGP Sessions",
                "unique_together": {("device", "local_address", "local_as", "remote_address", "remote_as")},
            },
        ),
    ]
