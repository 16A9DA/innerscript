from django.db import migrations
from django.utils.text import slugify

CATEGORIES = [
    "Anxiety",
    "Coping Tips",
    "Depression",
    "Relationships",
    "Self-care",
    "Student Life",
    "Vent",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    for name in CATEGORIES:
        Category.objects.get_or_create(
            slug=slugify(name), defaults={"name": name}
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    Category.objects.filter(slug__in=[slugify(n) for n in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0003_post_is_public"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
