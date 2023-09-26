# Generated by Django 4.2.4 on 2023-09-26 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ipam", "0064_clear_search_cache"),
        (
            "netbox_peering_manager",
            "0006_remove_bgpcommunity_netbox_peering_manager_bgpcommunity_value_site_uniq_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="bgppeergroup",
            name="local_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bgp_group_local_address_set",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AddField(
            model_name="bgppeergroup",
            name="local_as",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="local_bgp_peer_groups_set",
                to="ipam.asn",
            ),
        ),
        migrations.AddField(
            model_name="bgppeergroup",
            name="remote_as",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="remote_bgp_peer_groups_set",
                to="ipam.asn",
            ),
        ),
        migrations.AddField(
            model_name="bgppeergroup",
            name="status",
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="bgppeergroup",
            name="export_policies",
            field=models.ManyToManyField(
                blank=True, related_name="groups_export_policies_set", to="netbox_peering_manager.routingpolicy"
            ),
        ),
        migrations.AlterField(
            model_name="bgppeergroup",
            name="import_policies",
            field=models.ManyToManyField(
                blank=True, related_name="groups_import_policies_set", to="netbox_peering_manager.routingpolicy"
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="export_policies",
            field=models.ManyToManyField(
                blank=True, related_name="sessions_export_policies_set", to="netbox_peering_manager.routingpolicy"
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="import_policies",
            field=models.ManyToManyField(
                blank=True, related_name="sessions_import_policies_set", to="netbox_peering_manager.routingpolicy"
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="local_address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="local_address_session_set",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="local_as",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="local_as_bgp_session_set", to="ipam.asn"
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="remote_address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="remote_address_session_set",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AlterField(
            model_name="bgpsession",
            name="remote_as",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="remote_as_bgp_session_set", to="ipam.asn"
            ),
        ),
    ]
