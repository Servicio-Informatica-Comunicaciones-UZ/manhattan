# Generated by Django 4.0.3 on 2022-03-18 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0019_proyecto_descripcion_txt_alter_criterio_programas_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='financiacion_txt',
            field=models.TextField(null=True, verbose_name='Financiación en texto plano'),
        ),
    ]
