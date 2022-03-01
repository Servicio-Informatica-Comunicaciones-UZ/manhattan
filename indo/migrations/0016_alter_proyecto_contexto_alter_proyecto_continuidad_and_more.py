# Generated by Django 4.0.2 on 2022-03-01 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0015_alter_proyecto_descripcion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='contexto',
            field=models.TextField(
                blank=True,
                help_text='Otros proyectos de innovación relacionados con el propuesto, conocimiento que\n            se genera y marco epistemológico o teórico que lo avala y descripción del equipo de\n            trabajo para la realización del proyecto.',
                null=True,
                verbose_name='Contexto del proyecto',
            ),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='continuidad',
            field=models.TextField(
                blank=True,
                help_text='Transferibilidad, sostenibilidad y difusión prevista',
                null=True,
                verbose_name='Continuidad y Expansión',
            ),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='mejoras',
            field=models.TextField(
                blank=True,
                help_text='Método de evaluación, resultados e impacto (eficiencia y eficacia)',
                null=True,
                verbose_name='Mejoras esperadas en el proceso de enseñanza-aprendizaje y cómo se comprobarán.',
            ),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='metodos_estudio',
            field=models.TextField(
                blank=True,
                help_text='Métodos y técnicas utilizadas, características de la muestra, actividades previstas por los estudiantes y por el equipo del proyecto, así como calendario de actividades.',
                null=True,
                verbose_name='Métodos de estudio y trabajo de campo',
            ),
        ),
    ]
