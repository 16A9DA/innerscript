import os

from django.db import migrations


def set_site(apps, schema_editor):
    # allauth builds verification / reset emails from the Site record;
    # default is example.com. Point it at the real host (override via env).
    Site = apps.get_model("sites", "Site")
    domain = os.environ.get("SITE_DOMAIN", "innerscript.onrender.com")
    Site.objects.update_or_create(
        id=1, defaults={"domain": domain, "name": "InnerScript"}
    )


def unset_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(id=1).update(domain="example.com", name="example.com")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_profile_avatar"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [migrations.RunPython(set_site, unset_site)]
