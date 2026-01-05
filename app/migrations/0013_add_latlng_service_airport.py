from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0012_update_itinerarydestination_part_of_day_unicode"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="latitude",
            field=models.FloatField(blank=True, null=True, db_column="vi_do"),
        ),
        migrations.AddField(
            model_name="service",
            name="longitude",
            field=models.FloatField(blank=True, null=True, db_column="kinh_do"),
        ),
        migrations.AddField(
            model_name="airport",
            name="latitude",
            field=models.FloatField(blank=True, null=True, db_column="vi_do"),
        ),
        migrations.AddField(
            model_name="airport",
            name="longitude",
            field=models.FloatField(blank=True, null=True, db_column="kinh_do"),
        ),
    ]
