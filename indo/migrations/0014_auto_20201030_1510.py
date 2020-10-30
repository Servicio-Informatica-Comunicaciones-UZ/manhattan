# Generated by Django 3.1.2 on 2020-10-30 14:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('indo', '0013_auto_20201026_1053')]

    operations = [
        migrations.AlterModelOptions(
            name='memoriasubapartado',
            options={
                'ordering': ('apartado__numero', 'peso'),
                'verbose_name': 'subapartado de la memoria',
                'verbose_name_plural': 'subapartados de la memoria',
            },
        ),
        migrations.AlterField(
            model_name='memoriarespuesta',
            name='fichero',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='anexos_memoria/%Y/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])
                ],
                verbose_name='fichero PDF',
            ),
        ),
    ]
