from django.db import migrations

CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Other"]


def add_categories(apps, schema_editor):
    Category = apps.get_model("expenses", "Category")
    for name in CATEGORIES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model("expenses", "Category")
    Category.objects.filter(name__in=CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]