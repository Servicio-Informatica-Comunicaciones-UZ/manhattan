# Generated by Django 3.2 on 2021-05-10 11:28

from django.apps import apps as django_apps
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


def add_permission_to_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    gestores = Group.objects.get(name='Gestores')

    ver_up = Permission.objects.get(codename='ver_up')
    gestores.permissions.add(ver_up)


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0023_auto_20210506_1414'),
    ]

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
                    ('ver_memorias', 'Puede ver el listado y cualquier memoria de proyecto.'),
                    ('ver_up', 'Puede ver el listado de UP y gastos de los proyectos.'),
                ]
            },
        ),
        migrations.RunPython(migrate_permissions),
        migrations.RunPython(add_permission_to_group),
    ]