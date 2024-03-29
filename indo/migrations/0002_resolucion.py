# Generated by Django 3.1 on 2021-05-28 11:33

import datetime
from django.contrib.auth.management import create_permissions
from django.db import migrations, models


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


def add_permissions_to_groups(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    # Permisos para la interfaz de administración
    add_resolucion = Permission.objects.get(codename='add_resolucion')
    change_resolucion = Permission.objects.get(codename='change_resolucion')
    delete_resolucion = Permission.objects.get(codename='delete_resolucion')

    Group = apps.get_model('auth', 'Group')
    gestores = Group.objects.get(name='Gestores')
    gestores.permissions.add(add_resolucion, change_resolucion, delete_resolucion)


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resolucion',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('fecha', models.DateField(default=datetime.date.today)),
                ('titulo', models.CharField(max_length=255, verbose_name='título')),
                (
                    'url',
                    models.URLField(
                        help_text='Dirección de la página web. Vg: https://ae.unizar.es/?app=touz&opcion=mostrar&id=12345',
                        max_length=255,
                        verbose_name='URL',
                    ),
                ),
            ],
            options={
                'verbose_name': 'resolución',
                'verbose_name_plural': 'resoluciones',
                'ordering': ('fecha',),
            },
        ),
        migrations.RunPython(migrate_permissions),
        migrations.RunPython(add_permissions_to_groups),
    ]
