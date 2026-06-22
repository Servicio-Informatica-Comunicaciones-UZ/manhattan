from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0039_alter_proyecto_puntuacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='convocatoria',
            name='permite_colaboradores',
            field=models.BooleanField(default=False, verbose_name='¿Permite colaboradores?'),
        ),
    ]
