# Generated by Django 3.0.2 on 2020-02-07 08:19

from django.apps import apps as django_apps
from django.db import migrations, models


def add_permission_to_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    permission = apps.get_model('auth', 'Permission')

    gestores = group.objects.get(name='Gestores')
    ver_proyecto = permission.objects.get(codename='editar_proyecto')
    gestores.permissions.add(ver_proyecto)


def geo_post_migrate_signal(apps, schema_editor):
    '''Emit the post-migrate signal during the migration.

    Permissions are not actually created during or after an individual migration,
    but are triggered by a post-migrate signal which is sent after the
    `python manage.py migrate` command completes successfully.

    This is necessary because this permission is used later in this migration.
    '''
    indo_config = django_apps.get_app_config('indo')
    models.signals.post_migrate.send(
        sender=indo_config,
        app_config=indo_config,
        verbosity=2,
        interactive=False,
        using=schema_editor.connection.alias,
    )


class Migration(migrations.Migration):

    dependencies = [('indo', '0005_auto_20200203_1316')]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={
                'permissions': [
                    ('listar_proyectos', 'Puede ver el listado de todos los proyectos.'),
                    ('ver_proyecto', 'Puede ver cualquier proyecto.'),
                    ('editar_proyecto', 'Puede editar cualquier proyecto en cualquier momento.'),
                ]
            },
        ),
        migrations.RunPython(geo_post_migrate_signal),
        migrations.RunPython(add_permission_to_group),
    ]
