# Generated for netbox-peering-manager Phase 2: Peering Fabric

import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0215_rackreservation_status'),
        ('extras', '0133_make_cf_minmax_decimal'),
        ('ipam', '0082_add_prefix_network_containment_indexes'),
        ('tenancy', '0020_remove_contactgroupmembership'),
        ('netbox_peering_manager', '0038_alter_bfd_hold_time_alter_relationship_color'),
    ]

    operations = [
        # Create PeeringFabricType model
        migrations.CreateModel(
            name='PeeringFabricType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('color', models.CharField(default='9e9e9e', max_length=6)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Peering Fabric Type',
                'verbose_name_plural': 'Peering Fabric Types',
                'ordering': ['name'],
            },
        ),
        # Create PeeringFabric model
        migrations.CreateModel(
            name='PeeringFabric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(default='active', max_length=50)),
                ('peeringdb_id', models.PositiveIntegerField(blank=True, help_text='PeeringDB IX ID for integration', null=True)),
                ('comments', models.TextField(blank=True)),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fabrics', to='netbox_peering_manager.peeringfabrictype')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='peering_fabrics', to='dcim.site')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='peering_fabrics', to='tenancy.tenant')),
                ('peer_group', models.ForeignKey(blank=True, help_text='Default peer group for sessions on this fabric', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fabrics', to='netbox_peering_manager.bgppeergroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Peering Fabric',
                'verbose_name_plural': 'Peering Fabrics',
                'ordering': ['name'],
                'unique_together': {('name', 'site')},
            },
        ),
        # Create PeeringNetwork model
        migrations.CreateModel(
            name='PeeringNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default='active', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('fabric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='networks', to='netbox_peering_manager.peeringfabric')),
                ('prefix', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='peering_networks', to='ipam.prefix')),
                ('vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='peering_networks', to='ipam.vlan')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Peering Network',
                'verbose_name_plural': 'Peering Networks',
                'ordering': ['fabric', 'name'],
                'unique_together': {('fabric', 'name')},
            },
        ),
        # Create PeeringConnection model
        migrations.CreateModel(
            name='PeeringConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('status', models.CharField(default='active', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('peering_network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='netbox_peering_manager.peeringnetwork')),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='peering_connections', to='dcim.interface')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Peering Connection',
                'verbose_name_plural': 'Peering Connections',
                'ordering': ['peering_network', 'interface'],
                'unique_together': {('peering_network', 'interface')},
            },
        ),
        # Add peering_network to BGPSession
        migrations.AddField(
            model_name='bgpsession',
            name='peering_network',
            field=models.ForeignKey(
                blank=True,
                help_text='Peering network this session operates on (for fabric-based sessions)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='sessions',
                to='netbox_peering_manager.peeringnetwork',
            ),
        ),
    ]
