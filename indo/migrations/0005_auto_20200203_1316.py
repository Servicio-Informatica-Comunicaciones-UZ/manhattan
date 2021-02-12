# Generated by Django 3.0.2 on 2020-02-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('indo', '0004_auto_20200131_1409')]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={
                'permissions': [
                    ('listar_proyectos', 'Puede ver el listado de todos los proyectos.'),
                    ('ver_proyecto', 'Puede ver cualquier proyecto.'),
                ]
            },
        ),
        migrations.RenameField(
            model_name='programa',
            old_name='requiere_visto_bueno',
            new_name='requiere_visto_bueno_centro',
        ),
        migrations.RemoveField(model_name='proyecto', name='visto_bueno'),
        migrations.AddField(
            model_name='programa',
            name='requiere_visto_bueno_estudio',
            field=models.BooleanField(
                default='False',
                verbose_name='¿Requiere el visto bueno del coordinador del plan de estudios?',
            ),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='visto_bueno_centro',
            field=models.BooleanField(null=True, verbose_name='Visto bueno del centro'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='visto_bueno_estudio',
            field=models.BooleanField(null=True, verbose_name='Visto bueno del plan de estudios'),
        ),
    ]
