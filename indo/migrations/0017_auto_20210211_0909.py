# Generated by Django 3.1.5 on 2021-02-11 08:09

from django.apps import apps as django_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations, models


def add_permission_to_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    permission = apps.get_model('auth', 'Permission')

    gestores = group.objects.get(name='Gestores')

    permiso = permission.objects.get(codename='listar_evaluaciones')
    gestores.permissions.add(permiso)


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

    dependencies = [('indo', '0016_auto_20210203_1501')]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={
                'permissions': [
                    ('listar_proyectos', 'Puede ver el listado de todos los proyectos.'),
                    ('ver_proyecto', 'Puede ver cualquier proyecto.'),
                    ('editar_proyecto', 'Puede editar cualquier proyecto en cualquier momento.'),
                    (
                        'listar_evaluaciones',
                        'Puede ver el listado de evaluaciones de los proyectos.',
                    ),
                    ('listar_evaluadores', 'Puede ver el listado de evaluadores.'),
                    ('editar_evaluador', 'Puede editar el evaluador de un proyecto.'),
                    ('editar_aceptacion', 'Puede editar la decisión de la Comisión Evaluadora.'),
                    ('listar_correctores', 'Puede ver el listado de correctores.'),
                    ('editar_corrector', 'Puede modificar el corrector de un proyecto.'),
                ]
            },
        ),
        migrations.RunPython(migrate_permissions),
        migrations.RunPython(add_permission_to_group),
    ]