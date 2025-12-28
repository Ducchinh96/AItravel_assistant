from django.db import migrations


def forwards(apps, schema_editor):
    ItineraryDestination = apps.get_model("app", "ItineraryDestination")
    mapping = {
        "morning": "sáng",
        "afternoon": "chiều",
        "evening": "tối",
        "full_day": "cả ngày",
    }
    for old, new in mapping.items():
        ItineraryDestination.objects.filter(part_of_day=old).update(part_of_day=new)


def backwards(apps, schema_editor):
    ItineraryDestination = apps.get_model("app", "ItineraryDestination")
    mapping = {
        "sáng": "morning",
        "chiều": "afternoon",
        "tối": "evening",
        "cả ngày": "full_day",
    }
    for old, new in mapping.items():
        ItineraryDestination.objects.filter(part_of_day=old).update(part_of_day=new)


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0007_aidraftreview"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
