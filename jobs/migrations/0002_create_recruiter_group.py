from django.db import migrations


def create_recruiter_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Recruiter")


def delete_recruiter_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Recruiter").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0001_initial"),
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_recruiter_group, delete_recruiter_group),
    ]
