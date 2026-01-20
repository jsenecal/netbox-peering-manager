# Generated manually for issue #12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_peering_manager', '0002_add_database_indexes'),
    ]

    operations = [
        # Standardize related_name to "rules" for all rule models
        migrations.AlterField(
            model_name='aspathlistrule',
            name='aspath_list',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rules',
                to='netbox_peering_manager.aspathlist',
            ),
        ),
        migrations.AlterField(
            model_name='communitylistrule',
            name='community_list',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rules',
                to='netbox_peering_manager.communitylist',
            ),
        ),
        migrations.AlterField(
            model_name='prefixlistrule',
            name='prefix_list',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rules',
                to='netbox_peering_manager.prefixlist',
            ),
        ),
    ]
