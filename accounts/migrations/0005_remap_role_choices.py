from django.db import migrations

REMAP = {
    "youth": "student",
    "clinician": "mental_health_professional",
    "supporter": "advocate",
}


def remap_forward(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for old, new in REMAP.items():
        Profile.objects.filter(role=old).update(role=new)


def remap_backward(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for old, new in REMAP.items():
        Profile.objects.filter(role=new).update(role=old)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_profile_role"),
    ]

    operations = [
        migrations.RunPython(remap_forward, remap_backward),
    ]
