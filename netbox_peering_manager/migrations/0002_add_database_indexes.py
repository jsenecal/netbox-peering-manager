# Generated manually for issue #11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_peering_manager', '0001_initial'),
    ]

    operations = [
        # IRRSource.enabled - Sync job queries
        migrations.AlterField(
            model_name='irrsource',
            name='enabled',
            field=models.BooleanField(default=True, db_index=True),
        ),
        # PeerASN.affiliated - Filtering
        migrations.AlterField(
            model_name='peerasn',
            name='affiliated',
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text='ASN is operated by your organization (subsidiary, partner)',
            ),
        ),
        # PeerASN.peeringdb_last_sync - Sync queries
        migrations.AlterField(
            model_name='peerasn',
            name='peeringdb_last_sync',
            field=models.DateTimeField(null=True, blank=True, db_index=True),
        ),
        # PeeringNetwork.status - List filtering
        migrations.AlterField(
            model_name='peeringnetwork',
            name='status',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('planned', 'Planned'),
                    ('active', 'Active'),
                    ('disabled', 'Disabled'),
                ],
                default='active',
                db_index=True,
            ),
        ),
        # PeeringConnection.status - Filtering
        migrations.AlterField(
            model_name='peeringconnection',
            name='status',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('planned', 'Planned'),
                    ('active', 'Active'),
                    ('disabled', 'Disabled'),
                ],
                default='active',
                db_index=True,
            ),
        ),
        # BGPSession.name - Search
        migrations.AlterField(
            model_name='bgpsession',
            name='name',
            field=models.CharField(max_length=256, blank=True, null=True, db_index=True),
        ),
        # BGPSession.status - List filtering
        migrations.AlterField(
            model_name='bgpsession',
            name='status',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('planned', 'Planned'),
                    ('active', 'Active'),
                    ('disabled', 'Disabled'),
                    ('failed', 'Failed'),
                    ('offline', 'Offline'),
                    ('decommissioning', 'Decommissioning'),
                ],
                default='active',
                db_index=True,
            ),
        ),
    ]
