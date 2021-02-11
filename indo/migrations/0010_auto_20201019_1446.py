# Generated by Django 3.1.2 on 2020-10-19 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('indo', '0009_auto_20200622_0844')]

    operations = [
        migrations.AddField(
            model_name='convocatoria',
            name='fecha_max_aceptacion_resolucion',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha límite para confirmar la aceptación del proyecto admitido',
            ),
        ),
        migrations.AddField(
            model_name='convocatoria',
            name='fecha_max_alegaciones',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha límite para presentar alegaciones a la resolución de la comisión',
            ),
        ),
        migrations.AddField(
            model_name='convocatoria',
            name='fecha_max_gastos',
            field=models.DateField(
                blank=True, null=True, verbose_name='fecha límite para incorporar los gastos'
            ),
        ),
        migrations.AddField(
            model_name='convocatoria',
            name='fecha_max_memorias',
            field=models.DateField(
                blank=True, null=True, verbose_name='fecha límite para remitir la memoria final'
            ),
        ),
        migrations.AlterField(
            model_name='convocatoria',
            name='fecha_max_aceptos',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha límite para aceptar participar en un proyecto',
            ),
        ),
        migrations.AlterField(
            model_name='convocatoria',
            name='fecha_max_solicitudes',
            field=models.DateField(
                blank=True, null=True, verbose_name='fecha límite para presentar solicitudes'
            ),
        ),
        migrations.AlterField(
            model_name='convocatoria',
            name='fecha_max_visto_buenos',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha límite para que el decano/director dé el visto bueno a un proyecto',
            ),
        ),
        migrations.AlterField(
            model_name='convocatoria',
            name='fecha_min_solicitudes',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha en que se empiezan a aceptar solicitudes',
            ),
        ),
    ]