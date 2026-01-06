from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_peering_manager", "0039_peering_fabric"),
    ]

    operations = [
        migrations.CreateModel(
            name="IRRSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=None)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("url", models.URLField(help_text="fastbgpq4 API base URL (e.g., http://fastbgpq4:8000)")),
                ("sources", models.CharField(blank=True, help_text="Comma-separated IRR sources (e.g., RIPE,RADB,ARIN). Leave blank for default.", max_length=200)),
                ("cache_ttl", models.PositiveIntegerField(blank=True, help_text="Override default cache TTL in seconds", null=True)),
                ("sync_interval", models.PositiveIntegerField(default=1440, help_text="Minutes between automatic syncs (default: 1440 = 24 hours)")),
                ("enabled", models.BooleanField(default=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
                ("tags", models.ManyToManyField(blank=True, related_name="+", to="extras.tag")),
            ],
            options={
                "verbose_name": "IRR Source",
                "verbose_name_plural": "IRR Sources",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="prefixlist",
            name="source_as_set",
            field=models.CharField(blank=True, help_text="AS-SET to sync from IRR (e.g., AS-HURRICANE). When set, rules are managed by IRR sync.", max_length=100),
        ),
        migrations.AddField(
            model_name="prefixlist",
            name="irr_source",
            field=models.ForeignKey(blank=True, help_text="IRR source for AS-SET queries", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prefix_lists", to="netbox_peering_manager.irrsource"),
        ),
    ]
