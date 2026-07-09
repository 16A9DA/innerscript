from django.db import migrations
from django.utils.text import slugify

DESCRIPTIONS = {
    "Psychology & Neuroscience": "Discuss interesting concepts, ask questions, share research.",
    "Mental Health Education": "Talk about articles, myths, awareness campaigns, and educational resources.",
    "Wellbeing & Healthy Habits": "Evidence-based discussions on sleep, exercise, productivity, stress management, and routines.",
    "Research Corner": "Share and discuss new psychology, psychiatry, and neuroscience studies.",
    "Questions & Learning": "Ask mental health or psychology questions and learn from others. Not professional medical advice.",
    "Awareness & Advocacy": "Discuss stigma, public health initiatives, mental health policy, and awareness campaigns.",
    "Students & Careers": "Conversations about studying psychology, neuroscience, medicine, public health, or mental health careers.",
    "Book & Resource Recommendations": "Recommend books, podcasts, documentaries, and reputable educational resources.",
}


def set_descriptions(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    for name, desc in DESCRIPTIONS.items():
        Category.objects.filter(slug=slugify(name)).update(description=desc)


def clear_descriptions(apps, schema_editor):
    Category = apps.get_model("community", "Category")
    Category.objects.filter(
        slug__in=[slugify(n) for n in DESCRIPTIONS]
    ).update(description="")


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0005_reseed_education_categories"),
    ]

    operations = [
        migrations.RunPython(set_descriptions, clear_descriptions),
    ]
