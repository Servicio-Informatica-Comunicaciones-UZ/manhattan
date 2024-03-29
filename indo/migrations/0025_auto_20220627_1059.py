# Generated by Django 4.0.5 on 2022-06-27 08:59

from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_permissions_to_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    gestores = Group.objects.get(name='Gestores')
    ver_resolucion = Permission.objects.get(codename='ver_resolucion')
    gestores.permissions.add(ver_resolucion)


def migrate_permissions(apps, schema_editor):
    """Create the pending permissions.

    Permissions are not actually created during or after an individual migration,
    but are triggered by a post-migrate signal which is sent after the
    `python manage.py migrate` command completes successfully.

    This is necessary so that we can add the permission to a group in this migration.
    """
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=2)
        app_config.models_module = None


class Migration(migrations.Migration):

    dependencies = [('indo', '0024_alter_proyecto_options')]

    operations = [
        migrations.RunPython(migrate_permissions),
        migrations.RunPython(add_permissions_to_groups),
    ]
