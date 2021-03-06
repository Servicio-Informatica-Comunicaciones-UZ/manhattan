# Generated by Django 3.0.2 on 2020-01-22 09:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Centro',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('academico_id_nk', models.IntegerField(blank=True, null=True, verbose_name='cód. académico')),
                ('rrhh_id_nk', models.CharField(blank=True, max_length=4, null=True, verbose_name='cód. RRHH')),
                ('nombre', models.CharField(max_length=255)),
                ('tipo_centro', models.CharField(blank=True, max_length=30, null=True, verbose_name='tipo de centro')),
                ('direccion', models.CharField(blank=True, max_length=140, null=True, verbose_name='dirección')),
                ('municipio', models.CharField(blank=True, max_length=100, null=True)),
                ('telefono', models.CharField(blank=True, max_length=30, null=True, verbose_name='teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address')),
                ('url', models.URLField(blank=True, max_length=255, null=True, verbose_name='URL')),
                (
                    'nip_decano',
                    models.PositiveIntegerField(blank=True, null=True, verbose_name='NIP del decano o director'),
                ),
                (
                    'nombre_decano',
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name='nombre del decano o director'
                    ),
                ),
                (
                    'email_decano',
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name='email del decano o director'
                    ),
                ),
                (
                    'tratamiento_decano',
                    models.CharField(
                        blank=True, help_text='Decano/a ó director(a).', max_length=25, null=True, verbose_name='cargo'
                    ),
                ),
                (
                    'nip_secretario',
                    models.PositiveIntegerField(blank=True, null=True, verbose_name='NIP del secretario'),
                ),
                (
                    'nombre_secretario',
                    models.CharField(blank=True, max_length=255, null=True, verbose_name='nombre del secretario'),
                ),
                (
                    'email_secretario',
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del secretario'),
                ),
                (
                    'nips_coord_pou',
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name='NIPs de los coordinadores POU'
                    ),
                ),
                (
                    'nombres_coords_pou',
                    models.CharField(
                        blank=True, max_length=1023, null=True, verbose_name='nombres de los coordinadores POU'
                    ),
                ),
                (
                    'emails_coords_pou',
                    models.CharField(
                        blank=True, max_length=1023, null=True, verbose_name='emails de los coordinadores POU'
                    ),
                ),
                (
                    'unidad_gasto',
                    models.CharField(blank=True, max_length=3, null=True, verbose_name='unidad de gasto'),
                ),
                ('esta_activo', models.BooleanField(default=False, verbose_name='¿Activo?')),
            ],
            options={'ordering': ['nombre'], 'unique_together': {('academico_id_nk', 'rrhh_id_nk')}},
        ),
        migrations.CreateModel(
            name='Convocatoria',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='año')),
                ('num_max_equipos', models.PositiveSmallIntegerField(default=4)),
                ('fecha_min_solicitudes', models.DateField()),
                ('fecha_max_solicitudes', models.DateField()),
                ('fecha_max_aceptos', models.DateField()),
                ('fecha_max_visto_buenos', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                (
                    'academico_id_nk',
                    models.IntegerField(blank=True, db_index=True, null=True, verbose_name='cód. académico'),
                ),
                ('rrhh_id_nk', models.CharField(blank=True, max_length=4, null=True, verbose_name='cód. RRHH')),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                (
                    'email',
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del departamento'),
                ),
                (
                    'email_secretaria',
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name='email de la secretaría'),
                ),
                ('nip_director', models.PositiveIntegerField(blank=True, null=True, verbose_name='NIP del director')),
                (
                    'nombre_director',
                    models.CharField(blank=True, max_length=255, null=True, verbose_name='nombre del director'),
                ),
                (
                    'email_director',
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del director'),
                ),
                (
                    'unidad_gasto',
                    models.CharField(blank=True, max_length=3, null=True, verbose_name='unidad de gasto'),
                ),
            ],
            options={'unique_together': {('academico_id_nk', 'rrhh_id_nk')}},
        ),
        migrations.CreateModel(
            name='Estudio',
            fields=[
                (
                    'id',
                    models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='Cód. estudio'),
                ),
                ('nombre', models.CharField(max_length=255)),
                ('esta_activo', models.BooleanField(default=True, verbose_name='¿Activo?')),
                (
                    'rama',
                    models.CharField(
                        choices=[
                            ('B', 'Formación básica sin rama'),
                            ('H', 'Artes y Humanidades'),
                            ('J', 'Ciencias Sociales y Jurídicas'),
                            ('P', 'Títulos Propios'),
                            ('S', 'Ciencias de la Salud'),
                            ('T', 'Ingeniería y Arquitectura'),
                            ('X', 'Ciencias'),
                        ],
                        max_length=1,
                    ),
                ),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='Evento', fields=[('nombre', models.CharField(max_length=31, primary_key=True, serialize=False))]
        ),
        migrations.CreateModel(
            name='Licencia',
            fields=[
                (
                    'identificador',
                    models.CharField(
                        help_text='Ver los identificadores estándar en https://spdx.org/licenses/',
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('nombre', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, max_length=255, null=True, verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='Linea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=31)),
            ],
        ),
        migrations.CreateModel(
            name='Programa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_corto', models.CharField(help_text='Ejemplo: PRACUZ', max_length=15)),
                (
                    'nombre_largo',
                    models.CharField(
                        help_text='Ejemplo: Programa de Recursos en Abierto para Centros', max_length=127
                    ),
                ),
                (
                    'max_ayuda',
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name='Cuantía máxima que se puede solicitar de ayuda'
                    ),
                ),
                (
                    'max_estudiantes',
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name='Número máximo de estudiantes por programa'
                    ),
                ),
                ('campos', models.TextField(null=True)),
                (
                    'requiere_visto_bueno',
                    models.BooleanField(
                        default='False', verbose_name='¿Requiere el visto bueno del director o decano?'
                    ),
                ),
                (
                    'convocatoria',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Convocatoria'),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=31, null=True)),
                ('titulo', models.CharField(max_length=255, verbose_name='Título')),
                (
                    'descripcion',
                    models.TextField(
                        help_text='Resumen sucinto del proyecto. Máximo recomendable: un párrafo de 10 líneas.',
                        max_length=4095,
                        null=True,
                        verbose_name='Descripción',
                    ),
                ),
                (
                    'estado',
                    models.CharField(
                        choices=[
                            ('ANULADO', 'Solicitud anulada'),
                            ('BORRADOR', 'Solicitud en preparación'),
                            ('SOLICITADO', 'Solicitud presentada'),
                        ],
                        default='BORRADOR',
                        max_length=63,
                    ),
                ),
                (
                    'contexto',
                    models.TextField(
                        blank=True,
                        help_text='Necesidad a la que responde el proyecto, mejoras esperadas respecto al estado de la cuestión, conocimiento que se genera.',
                        null=True,
                        verbose_name='Contexto del proyecto',
                    ),
                ),
                ('objetivos', models.TextField(blank=True, null=True, verbose_name='Objetivos del Proyecto')),
                (
                    'metodos_estudio',
                    models.TextField(
                        blank=True,
                        help_text='Métodos/técnicas utilizadas, características de la muestra, actividades previstas por los estudiantes y por el equipo del proyecto, calendario de actividades.',
                        null=True,
                        verbose_name='Métodos de estudio/experimentación y trabajo de campo',
                    ),
                ),
                (
                    'mejoras',
                    models.TextField(
                        blank=True,
                        help_text='Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)',
                        null=True,
                        verbose_name='Mejoras esperadas en el proceso de enseñanza-aprendizaje y cómo se comprobarán.',
                    ),
                ),
                (
                    'continuidad',
                    models.TextField(
                        blank=True,
                        help_text='Transferibilidad, Sostenibilidad, Difusión prevista',
                        null=True,
                        verbose_name='Continuidad y Expansión',
                    ),
                ),
                (
                    'tipo',
                    models.TextField(
                        blank=True,
                        help_text='Experiencia, Estudio o Desarrollo',
                        null=True,
                        verbose_name='Tipo de proyecto',
                    ),
                ),
                (
                    'contexto_aplicacion',
                    models.TextField(
                        blank=True,
                        help_text='Centro, titulación, curso...',
                        null=True,
                        verbose_name='Contexto de aplicación/Público objetivo',
                    ),
                ),
                (
                    'metodos',
                    models.TextField(blank=True, null=True, verbose_name='Métodos/Técnicas/Actividades utilizadas'),
                ),
                ('tecnologias', models.TextField(blank=True, null=True, verbose_name='Tecnologías utilizadas')),
                (
                    'aplicacion',
                    models.TextField(
                        blank=True, null=True, verbose_name='Posible aplicación a otros centros/áreas de conocimiento'
                    ),
                ),
                (
                    'proyectos_anteriores',
                    models.TextField(
                        blank=True,
                        help_text='Nombres de los proyectos de innovación realizados en cursos anteriores que estén relacionados con la temática propuesta.',
                        null=True,
                        verbose_name='Proyectos anteriores',
                    ),
                ),
                ('impacto', models.TextField(blank=True, null=True, verbose_name='Impacto del proyecto')),
                ('innovacion', models.TextField(blank=True, null=True, verbose_name='Tipo de innovación introducida')),
                (
                    'interes',
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name='Interés y oportunidad para la institución/titulación/centro',
                    ),
                ),
                (
                    'justificacion_equipo',
                    models.TextField(
                        blank=True,
                        help_text='Experiencia común conjunta, experiencia previa en el tipo de curso solicitado, etc.',
                        null=True,
                        verbose_name='Justificación del equipo docente que conforma la solicitud',
                    ),
                ),
                (
                    'caracter_estrategico',
                    models.TextField(blank=True, null=True, verbose_name='Carácter estratégico del curso para la UZ'),
                ),
                (
                    'seminario',
                    models.TextField(blank=True, null=True, verbose_name='Asignatura, curso, seminario o equivalente'),
                ),
                ('idioma', models.TextField(blank=True, null=True, verbose_name='Idioma de publicación')),
                ('ramas', models.TextField(blank=True, null=True, verbose_name='Ramas de conocimiento')),
                (
                    'mejoras_pou',
                    models.TextField(
                        blank=True,
                        help_text='Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)',
                        null=True,
                        verbose_name='Mejoras esperadas en el Plan de Orientación Universitaria y cómo se comprobarán.',
                    ),
                ),
                (
                    'ambito',
                    models.TextField(
                        blank=True,
                        help_text="Consultar las áreas en el bloque derecho de <a href='https://ocw.unizar.es/ocw/course/index.php?categoryid=8' target='_blank'>https://ocw.unizar.es/ocw/course/index.php?categoryid=8</a>.",
                        null=True,
                        verbose_name='Ámbito o ámbitos correspondientes a su área de conocimiento',
                    ),
                ),
                (
                    'contenidos',
                    models.TextField(
                        blank=True,
                        help_text='Para OCW indicar los temas, que incluirán teoría, problemas, autoevaluación, etc.',
                        null=True,
                        verbose_name='Breve descripción de los contenidos',
                    ),
                ),
                (
                    'afectadas',
                    models.TextField(blank=True, null=True, verbose_name='Asignatura/s y Titulación/es afectadas'),
                ),
                (
                    'formatos',
                    models.TextField(blank=True, null=True, verbose_name='Formatos de los materiales incluidos.'),
                ),
                (
                    'enlace',
                    models.TextField(
                        blank=True,
                        help_text='Incluir el enlace (o enlaces) a la página de los estudios en la que se encuentra el plan de mejora y una mención expresa a qué aspecto del mismo se refiere el proyecto.',
                        null=True,
                        verbose_name='Enlace',
                    ),
                ),
                (
                    'contenido_modulos',
                    models.TextField(
                        blank=True,
                        help_text='Los cursos 0 deberán incluir un capítulo 0 con las competencias demandadas al alumnado que va a comenzar el estudio o estudios objeto del curso.',
                        null=True,
                        verbose_name='Breve descripción de los contenidos de cada capítulo/módulo',
                    ),
                ),
                (
                    'material_previo',
                    models.TextField(
                        blank=True, null=True, verbose_name='Indicar si se cuenta con algún material previo'
                    ),
                ),
                (
                    'duracion',
                    models.TextField(
                        blank=True,
                        help_text='Número de semanas y número de horas de estudio y trabajo autónomo del participante en todo el curso.',
                        null=True,
                        verbose_name='Duración del curso',
                    ),
                ),
                (
                    'multimedia',
                    models.TextField(
                        blank=True,
                        help_text='Elementos multimedia e innovadores que va a utilizar en la elaboración del curso.',
                        null=True,
                        verbose_name='Elementos multimedia e innovadores',
                    ),
                ),
                (
                    'indicadores',
                    models.TextField(
                        blank=True, null=True, verbose_name='Indicadores para el seguimiento y evaluación del curso'
                    ),
                ),
                (
                    'actividades',
                    models.TextField(
                        blank=True,
                        help_text='Sólo obligatorias para MOOCs.',
                        null=True,
                        verbose_name='Actividades de dinamización previstas',
                    ),
                ),
                (
                    'financiacion',
                    models.TextField(
                        blank=True,
                        help_text='Justificar la necesidad de lo solicitado. Añadir información sobre otras fuentes de financiación.',
                        null=True,
                        verbose_name='Financiación',
                    ),
                ),
                (
                    'ayuda',
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        help_text='Las normas de la convocatoria establecen el importe máximo que se puede solicitar según el programa.',
                        null=True,
                        verbose_name='Ayuda económica solicitada',
                    ),
                ),
                ('visto_bueno', models.BooleanField(null=True, verbose_name='Visto bueno')),
                (
                    'centro',
                    models.ForeignKey(
                        blank=True,
                        help_text='Sólo obligatorio para PIEC, PRACUZ, PIPOUZ.',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='proyectos',
                        to='indo.Centro',
                    ),
                ),
                (
                    'convocatoria',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Convocatoria'),
                ),
                (
                    'departamento',
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='indo.Departamento'),
                ),
                (
                    'estudio',
                    models.ForeignKey(
                        blank=True,
                        help_text='Sólo obligatorio para PIET.',
                        limit_choices_to={'esta_activo': True},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to='indo.Estudio',
                    ),
                ),
                (
                    'licencia',
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='indo.Licencia'),
                ),
                (
                    'linea',
                    models.ForeignKey(
                        blank=True,
                        help_text='En su caso.',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to='indo.Linea',
                        verbose_name='Línea',
                    ),
                ),
                ('programa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Programa')),
            ],
        ),
        migrations.CreateModel(
            name='TipoEstudio',
            fields=[
                (
                    'id',
                    models.PositiveSmallIntegerField(
                        primary_key=True, serialize=False, verbose_name='Cód. tipo estudio'
                    ),
                ),
                ('nombre', models.CharField(max_length=63)),
            ],
        ),
        migrations.CreateModel(
            name='TipoParticipacion',
            fields=[('nombre', models.CharField(max_length=63, primary_key=True, serialize=False))],
        ),
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.CharField(max_length=255)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Evento')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_nk', models.PositiveSmallIntegerField(verbose_name='Cód. plan')),
                (
                    'nip_coordinador',
                    models.PositiveIntegerField(blank=True, null=True, verbose_name='NIP del coordinador'),
                ),
                (
                    'nombre_coordinador',
                    models.CharField(blank=True, max_length=255, null=True, verbose_name='nombre del coordinador'),
                ),
                (
                    'email_coordinador',
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name='email del coordinador'),
                ),
                ('esta_activo', models.BooleanField(default=True, verbose_name='¿Activo?')),
                ('centro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Centro')),
                ('estudio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.Estudio')),
            ],
        ),
        migrations.CreateModel(
            name='ParticipanteProyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'proyecto',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='participantes', to='indo.Proyecto'
                    ),
                ),
                (
                    'tipo_participacion',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.TipoParticipacion'),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='vinculaciones',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='linea',
            name='programa',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='lineas', to='indo.Programa'
            ),
        ),
        migrations.AddField(
            model_name='estudio',
            name='tipo_estudio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='indo.TipoEstudio'),
        ),
    ]
