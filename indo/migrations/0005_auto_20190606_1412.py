# Generated by Django 2.2.1 on 2019-06-06 12:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("indo", "0004_auto_20190605_1105")]

    operations = [
        migrations.AddField(
            model_name="convocatoria",
            name="num_max_equipos",
            field=models.PositiveSmallIntegerField(default=4),
        ),
        migrations.AlterField(
            model_name="participanteproyecto",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="vinculaciones",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]