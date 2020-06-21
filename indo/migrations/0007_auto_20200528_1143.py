# Generated by Django 3.0.6 on 2020-05-28 09:43

from django.apps import apps as django_apps
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def add_permissions_to_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    permission = apps.get_model('auth', 'Permission')

    gestores = group.objects.get(name='Gestores')
    permiso = permission.objects.get(codename='listar_evaluadores')
    gestores.permissions.add(permiso)
    permiso = permission.objects.get(codename='editar_evaluador')
    gestores.permissions.add(permiso)


def create_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    group, created = group.objects.get_or_create(name='Evaluadores')


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

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('indo', '0006_auto_20200207_0919'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={
                'permissions': [
                    ('listar_proyectos', 'Puede ver el listado de todos los proyectos.'),
                    ('ver_proyecto', 'Puede ver cualquier proyecto.'),
                    ('editar_proyecto', 'Puede editar cualquier proyecto en cualquier momento.'),
                    ('listar_evaluadores', 'Puede ver el listado de evaluadores.'),
                    ('editar_evaluador', 'Puede editar el evaluador de un proyecto.'),
                ]
            },
        ),
        migrations.AddField(
            model_name='proyecto',
            name='evaluador',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='proyectos_evaluados',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(geo_post_migrate_signal),
        migrations.RunPython(add_permissions_to_group),
        migrations.RunPython(create_group),
        migrations.RunPython(geo_post_migrate_signal),
    ]