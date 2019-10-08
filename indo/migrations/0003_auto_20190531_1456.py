# Generated by Django 2.2.1 on 2019-05-31 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("indo", "0002_auto_20190405_1408")]

    operations = [
        migrations.AlterField(
            model_name="linea",
            name="programa",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="lineas",
                to="indo.Programa",
            ),
        ),
        migrations.AlterField(
            model_name="participanteproyecto",
            name="proyecto",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participantes",
                to="indo.Proyecto",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="ayuda",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="Las normas de la convocatoria establecen el importe máximo que se puede solicitar según el programa.",  # noqa
                null=True,
                verbose_name="Ayuda económica solicitada",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="contexto",
            field=models.TextField(
                blank=True,
                help_text="Necesidad a la que responde el proyecto, mejoras esperadas respecto al estado de la cuestión, conocimiento que se genera.",  # noqa
                null=True,
                verbose_name="Contexto del proyecto",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="estado",
            field=models.CharField(
                choices=[
                    ("BORRADOR", "Solicitud en preparación"),
                    ("SOLICITADO", "Solicitud presentada"),
                ],
                default="BORRADOR",
                max_length=63,
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="financiacion",
            field=models.TextField(
                blank=True,
                help_text="Justificar la necesidad de lo solicitado. Añadir información sobre otras fuentes de financiación.",  # noqa
                null=True,
                verbose_name="Financiación",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="mejoras",
            field=models.TextField(
                blank=True,
                help_text="Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)",  # noqa
                null=True,
                verbose_name="Mejoras esperadas en el proceso de enseñanza-aprendizaje y cómo se comprobarán.",  # noqa
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="mejoras_pou",
            field=models.TextField(
                blank=True,
                help_text="Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)",  # noqa
                null=True,
                verbose_name="Mejoras esperadas en el Plan de Orientación Universitaria y cómo se comprobarán.",  # noqa
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="metodos_estudio",
            field=models.TextField(
                blank=True,
                help_text="Métodos/técnicas utilizadas, características de la muestra, actividades previstas por los estudiantes y por el equipo del proyecto, calendario de actividades.",  # noqa
                null=True,
                verbose_name="Métodos de estudio/experimentación y trabajo de campo",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="multimedia",
            field=models.TextField(
                blank=True,
                help_text="Elementos multimedia e innovadores que va a utilizar en la elaboración del curso.",  # noqa
                null=True,
                verbose_name="Elementos multimedia e innovadores",
            ),
        ),
        migrations.AlterField(
            model_name="proyecto",
            name="proyectos_anteriores",
            field=models.TextField(
                blank=True,
                help_text="Nombres de los proyectos de innovación realizados en cursos anteriores que estén relacionados con la temática propuesta.",  # noqa
                null=True,
                verbose_name="Proyectos anteriores",
            ),
        ),
    ]