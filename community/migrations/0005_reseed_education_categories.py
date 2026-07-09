from django.db import migrations
from django.utils.text import slugify

OLD = [
    "Anxiety",
    "Coping Tips",
    "Depression",
    "Relationships",
    "Self-care",
    "Student Life",
    "Vent",
]

NEW = [
    "Psychology & Neuroscience",
    "Mental Health Education",
    "Wellbeing & Healthy Habits",
    "Research Corner",
    "Questions & Learning",
    "Awareness & Advocacy",
    "Students & Careers",
    "Book & Resource Recommendations",
]


def reseed(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    Category.objects.filter(slug__in=[slugify(n) for n in OLD]).delete()
    for name in NEW:
        Category.objects.get_or_create(slug=slugify(name), defaults={"name": name})


def revert(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    Category.objects.filter(slug__in=[slugify(n) for n in NEW]).delete()
    for name in OLD:
        Category.objects.get_or_create(slug=slugify(name), defaults={"name": name})


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0004_seed_categories"),
    ]

    operations = [
        migrations.RunPython(reseed, revert),
    ]
