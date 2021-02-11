# Generated by Django 3.1.2 on 2020-10-26 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('indo', '0012_auto_20201023_1034')]

    operations = [
        migrations.CreateModel(
            name='MemoriaApartado',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('numero', models.PositiveSmallIntegerField(verbose_name='número')),
                ('descripcion', models.CharField(max_length=255, verbose_name='descripción')),
            ],
            options={
                'verbose_name': 'apartado de la memoria',
                'verbose_name_plural': 'apartados de la memoria',
                'ordering': ('convocatoria__id', 'numero'),
            },
        ),
        migrations.AlterModelOptions(name='convocatoria', options={'ordering': ('-id',)}),
        migrations.AddField(
            model_name='proyecto',
            name='aceptacion_corrector',
            field=models.BooleanField(null=True, verbose_name='Aceptación por el corrector'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='observaciones_corrector',
            field=models.TextField(
                null=True, verbose_name='Observaciones del corrector de la memoria'
            ),
        ),
        migrations.AlterField(
            model_name='criterio',
            name='descripcion',
            field=models.CharField(max_length=255, verbose_name='descripción'),
        ),
        migrations.CreateModel(
            name='MemoriaSubapartado',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('peso', models.PositiveSmallIntegerField(verbose_name='peso')),
                ('descripcion', models.CharField(max_length=255, verbose_name='descripción')),
                ('ayuda', models.CharField(max_length=255, verbose_name='texto de ayuda')),
                (
                    'tipo',
                    models.CharField(
                        choices=[('texto', 'Texto libre'), ('fichero', 'Fichero')],
                        max_length=15,
                        verbose_name='tipo',
                    ),
                ),
                (
                    'apartado',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='subapartados',
                        to='indo.memoriaapartado',
                    ),
                ),
            ],
            options={
                'verbose_name': 'apartado de la memoria',
                'verbose_name_plural': 'apartados de la memoria',
                'ordering': ('apartado__id', 'peso'),
            },
        ),
        migrations.CreateModel(
            name='MemoriaRespuesta',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('texto', models.TextField(blank=True, null=True, verbose_name='texto')),
                (
                    'fichero',
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to='anexos_memoria',
                        verbose_name='fichero PDF',
                    ),
                ),
                (
                    'proyecto',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='respuestas_memoria',
                        to='indo.proyecto',
                    ),
                ),
                (
                    'subapartado',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='respuestas',
                        to='indo.memoriasubapartado',
                    ),
                ),
            ],
            options={
                'verbose_name': 'respuesta de la memoria',
                'verbose_name_plural': 'respuestas de la memoria',
                'ordering': ('-proyecto__id', 'subapartado'),
            },
        ),
        migrations.AddField(
            model_name='memoriaapartado',
            name='convocatoria',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='apartados_memoria',
                to='indo.convocatoria',
            ),
        ),
    ]