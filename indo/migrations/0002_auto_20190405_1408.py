# Generated by Django 2.1 on 2019-04-05 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('indo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('academico_id_nk', models.IntegerField(blank=True, db_index=True, null=True, verbose_name='cód. académico')),
                ('rrhh_id_nk', models.CharField(blank=True, max_length=4, null=True, unique=True, verbose_name='cód. RRHH')),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del departamento')),
                ('email_secretaria', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email de la secretaría')),
                ('nip_director', models.PositiveIntegerField(blank=True, null=True, verbose_name='NIP del director')),
                ('nombre_director', models.CharField(blank=True, max_length=255, null=True, verbose_name='nombre del director')),
                ('email_director', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del director')),
            ],
        ),
        migrations.AddField(
            model_name='programa',
            name='campos',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='actividades',
            field=models.TextField(blank=True, help_text='Sólo obligatorias para MOOCs.', null=True, verbose_name='Actividades de dinamización previstas'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='afectadas',
            field=models.TextField(blank=True, null=True, verbose_name='Asignatura/s y Titulación/es afectadas'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='ambito',
            field=models.TextField(blank=True, help_text="Consultar las áreas en el bloque derecho de <a href='https://ocw.unizar.es/ocw/course/index.php?categoryid=8' target='_blank'>https://ocw.unizar.es/ocw/course/index.php?categoryid=8</a>.", null=True, verbose_name='Ámbito o ámbitos correspondientes a su área de conocimiento'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='aplicacion',
            field=models.TextField(blank=True, null=True, verbose_name='Posible aplicación a otros centros/áreas de conocimiento'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='caracter_estrategico',
            field=models.TextField(blank=True, null=True, verbose_name='Carácter estratégico del curso para la UZ'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='contenido_modulos',
            field=models.TextField(blank=True, help_text='Los cursos 0 deberán incluir un capítulo 0 con las competencias demandadas al alumnado que va a comenzar el estudio o estudios objeto del curso.', null=True, verbose_name='Breve descripción de los contenidos de cada capítulo/módulo'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='contenidos',
            field=models.TextField(blank=True, help_text='Para OCW indicar los temas, que incluirán teoría, problemas, autoevaluación, etc.', null=True, verbose_name='Breve descripción de los contenidos'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='contexto',
            field=models.TextField(blank=True, help_text='Necesidad a la que responde el proyecto, mejoras esperadas respecto al estado de la cuestión, conocimiento que se genera', null=True, verbose_name='Contexto del proyecto'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='contexto_aplicacion',
            field=models.TextField(blank=True, help_text='Centro, titulación, curso...', null=True, verbose_name='Contexto de aplicación/Público objetivo'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='continuidad',
            field=models.TextField(blank=True, help_text='Transferibilidad, Sostenibilidad, Difusión prevista', null=True, verbose_name='Continuidad y Expansión'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='duracion',
            field=models.TextField(blank=True, help_text='Número de semanas y número de horas de estudio y trabajo autónomo del participante en todo el curso.', null=True, verbose_name='Duración del curso'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='enlace',
            field=models.TextField(blank=True, help_text='Incluir el enlace (o enlaces) a la página de los estudios en la que se encuentra el plan de mejora y una mención expresa a qué aspecto del mismo se refiere el proyecto.', null=True, verbose_name='Enlace'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='estado',
            field=models.CharField(choices=[('BORRADOR', 'Solicitud en preparación'), ('SOLICITADO', 'Solicitud presentada')], default='BORRADOR', max_length=63),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='formatos',
            field=models.TextField(blank=True, null=True, verbose_name='Formatos de los materiales incluidos.'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='idioma',
            field=models.TextField(blank=True, null=True, verbose_name='Idioma de publicación'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='impacto',
            field=models.TextField(blank=True, null=True, verbose_name='Impacto del proyecto'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='indicadores',
            field=models.TextField(blank=True, null=True, verbose_name='Indicadores para el seguimiento y evaluación del curso'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='innovacion',
            field=models.TextField(blank=True, null=True, verbose_name='Tipo de innovación introducida'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='interes',
            field=models.TextField(blank=True, null=True, verbose_name='Interés y oportunidad para la institución/titulación/centro'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='justificacion_equipo',
            field=models.TextField(blank=True, help_text='Experiencia común conjunta, experiencia previa en el tipo de curso solicitado, etc.', null=True, verbose_name='Justificación del equipo docente que conforma la solicitud'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='material_previo',
            field=models.TextField(blank=True, null=True, verbose_name='Indicar si se cuenta con algún material previo'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='mejoras',
            field=models.TextField(blank=True, help_text='Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)', null=True, verbose_name='Mejoras esperadas en el proceso de enseñanza-aprendizaje y cómo se comprobarán'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='mejoras_pou',
            field=models.TextField(blank=True, help_text='Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)', null=True, verbose_name='Mejoras esperadas en el Plan de Orientación Universitaria y cómo se comprobarán'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='metodos',
            field=models.TextField(blank=True, null=True, verbose_name='Métodos/Técnicas/Actividades utilizadas'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='metodos_estudio',
            field=models.TextField(blank=True, help_text='Métodos/técnicas utilizadas, características de la muestra, actividades previstas por los estudiantes y por el equipo del proyecto, calendario de actividades', null=True, verbose_name='Métodos de estudio/experimentación y trabajo de campo'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='multimedia',
            field=models.TextField(blank=True, help_text='Elementos multimedia e innovadores que va a utilizar en la elaboración del curso', null=True, verbose_name='Elementos multimedia e innovadores'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='objetivos',
            field=models.TextField(blank=True, null=True, verbose_name='Objetivos del Proyecto'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='proyectos_anteriores',
            field=models.TextField(blank=True, help_text='Nombres de los proyectos de innovación realizados en cursos anteriores que estén relacionados con la temática propuesta', null=True, verbose_name='Proyectos anteriores'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='ramas',
            field=models.TextField(blank=True, null=True, verbose_name='Ramas de conocimiento'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='seminario',
            field=models.TextField(blank=True, null=True, verbose_name='Asignatura, curso, seminario o equivalente'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tecnologias',
            field=models.TextField(blank=True, null=True, verbose_name='Tecnologías utilizadas'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipo',
            field=models.TextField(blank=True, help_text='Experiencia, Estudio o Desarrollo', null=True, verbose_name='Tipo de proyecto'),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='financiacion',
            field=models.TextField(blank=True, help_text='Justificar la necesidad de lo solicitado e indicar el importe, siguiendo las normas de la convocatoria. Añadir información sobre otras fuentes de financiación', null=True, verbose_name='Financiación solicitada'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='departamento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='indo.Departamento'),
        ),
    ]
