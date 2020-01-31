# Generated by Django 3.0.2 on 2020-01-31 11:45
# https://docs.djangoproject.com/en/3.0/howto/writing-migrations/

from django.apps import apps as django_apps
from django.db import migrations, models


def add_managers_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, created = Group.objects.get_or_create(name="Gestores")
    if created:
        print("Creado el grupo «Gestores».")
        listar_proyectos = Permission.objects.get(codename="listar_proyectos")
        group.permissions.add(listar_proyectos)


def geo_post_migrate_signal(apps, schema_editor):
    """Emit the post-migrate signal during the migration.

    Permissions are not actually created during or after an individual migration,
    but are triggered by a post-migrate signal which is sent after the
    `python manage.py migrate` command completes successfully.

    This is necessary because this permission is used in the next migration.
    """
    indo_config = django_apps.get_app_config("indo")
    models.signals.post_migrate.send(
        sender=indo_config,
        app_config=indo_config,
        verbosity=2,
        interactive=False,
        using=schema_editor.connection.alias,
    )


class Migration(migrations.Migration):

    dependencies = [("indo", "0002_auto_20200131_1244")]

    operations = [
        migrations.RunPython(add_managers_group),
        migrations.RunPython(geo_post_migrate_signal),
    ]
