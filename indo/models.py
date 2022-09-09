# Standard library
from __future__ import annotations
import datetime

# Django
from django.core.validators import FileExtensionValidator
from django.db import connection, models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Centro(models.Model):
    id = models.AutoField(primary_key=True)
    academico_id_nk = models.IntegerField(_('cód. académico'), blank=True, null=True)
    rrhh_id_nk = models.CharField(_('cód. RRHH'), max_length=4, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    tipo_centro = models.CharField(_('tipo de centro'), max_length=30, blank=True, null=True)
    direccion = models.CharField(_('dirección'), max_length=140, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(_('teléfono'), max_length=30, blank=True, null=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    url = models.URLField('URL', max_length=255, blank=True, null=True)
    nip_decano = models.PositiveIntegerField(_('NIP del decano o director'), blank=True, null=True)
    nombre_decano = models.CharField(
        _('nombre del decano o director'), max_length=255, blank=True, null=True
    )
    email_decano = models.EmailField(_('email del decano o director'), blank=True, null=True)
    tratamiento_decano = models.CharField(
        _('cargo'), max_length=25, blank=True, null=True, help_text=_('Decano/a ó director(a).')
    )
    nip_secretario = models.PositiveIntegerField(_('NIP del secretario'), blank=True, null=True)
    nombre_secretario = models.CharField(
        _('nombre del secretario'), max_length=255, blank=True, null=True
    )
    email_secretario = models.EmailField(_('email del secretario'), blank=True, null=True)
    email_administrador = models.EmailField(_('email del administrador'), default='', null=True)
    nips_coord_pou = models.CharField(
        _('NIPs de los coordinadores POU'), blank=True, max_length=255, null=True
    )
    nombres_coords_pou = models.CharField(
        _('nombres de los coordinadores POU'), blank=True, max_length=1023, null=True
    )
    emails_coords_pou = models.CharField(
        _('emails de los coordinadores POU'), blank=True, max_length=1023, null=True
    )
    unidad_planificacion = models.CharField(
        _('unidad de planificación'), blank=True, max_length=3, null=True
    )
    esta_activo = models.BooleanField(_('¿Activo?'), default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['academico_id_nk', 'rrhh_id_nk'], name="centro-unique-academico-rrhh"
            )
        ]
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.academico_id_nk} / {self.rrhh_id_nk})'


class Convocatoria(models.Model):
    id = models.PositiveSmallIntegerField(_('año'), primary_key=True)
    num_max_equipos = models.PositiveSmallIntegerField(
        _('número máximo de equipos en que puede participar una persona'), default=4
    )
    fecha_min_solicitudes = models.DateField(
        _('fecha en que se empiezan a aceptar solicitudes'), blank=True, null=True
    )
    fecha_max_solicitudes = models.DateField(
        _('fecha límite para presentar solicitudes'), blank=True, null=True
    )
    fecha_max_aceptos = models.DateField(
        _('fecha límite para aceptar participar en un proyecto'), blank=True, null=True
    )
    fecha_max_visto_buenos = models.DateField(
        _('fecha límite para que el decano/director dé el visto bueno a un proyecto'),
        blank=True,
        null=True,
    )
    fecha_max_alegaciones = models.DateField(
        _('fecha límite para presentar alegaciones a la resolución de la comisión'),
        blank=True,
        null=True,
    )
    fecha_max_aceptacion_resolucion = models.DateField(
        _('fecha límite para confirmar la aceptación del proyecto admitido'), blank=True, null=True
    )
    fecha_max_modificacion_equipos = models.DateField(
        _('fecha límite para modificaciones excepcionales de los equipos de trabajo'),
        blank=True,
        null=True,
    )
    fecha_max_memorias = models.DateField(
        _('fecha límite para remitir la memoria final'), blank=True, null=True
    )
    fecha_max_gastos = models.DateField(
        _('fecha límite para incorporar los gastos'), blank=True, null=True
    )
    notificada_resolucion_provisional = models.BooleanField(default=False)
    notificada_resolucion_definitiva = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return str(f'{self.id}-{self.id + 1}')

    @classmethod
    def get_ultima(cls) -> Convocatoria:
        """Devuelve la última convocatoria."""

        ultima_convocatoria = Convocatoria.objects.order_by('-id').first()
        if not ultima_convocatoria:
            raise Convocatoria.DoesNotExist
        return ultima_convocatoria


class Criterio(models.Model):
    """Criterios para evaluar proyectos por la ACPUA."""

    class Tipo(models.TextChoices):
        """Tipo de criterio.

        Los criterios pueden ser de dos tipos:

        * Opción - Se debe elegir una de las opciones predefinidas, con su puntuación asignada.
        * Texto libre - El evaluador puede introducir un texto con sus comentarios.
        """

        OPCION = 'opcion', _('Opción')
        TEXTO = 'texto', _('Texto libre')

    convocatoria = models.ForeignKey('Convocatoria', on_delete=models.PROTECT)
    programas = models.JSONField(
        _('programas en los que aplicar este criterio'),
        default=list,
        help_text=_(
            '''Nombre de los programas entrecomillados, separados por comas,
            y todos ellos entre corchetes.<br>
            Ejemplo: <span style="font-family: monospace;">["PIIDUZ", "PIET"]</span>'''
        ),
    )
    parte = models.PositiveSmallIntegerField(_('parte'))
    peso = models.PositiveSmallIntegerField(_('peso'))
    descripcion = models.CharField(_('descripción'), max_length=255)
    tipo = models.CharField(_('tipo'), max_length=15, choices=Tipo.choices)

    class Meta:
        ordering = ('convocatoria', 'parte', 'peso')

    def __str__(self):
        return self.descripcion


class Departamento(models.Model):
    id = models.AutoField(primary_key=True)
    academico_id_nk = models.IntegerField('cód. académico', blank=True, db_index=True, null=True)
    rrhh_id_nk = models.CharField('cód. RRHH', max_length=4, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(_('email del departamento'), blank=True, null=True)
    email_secretaria = models.EmailField(_('email de la secretaría'), blank=True, null=True)
    nip_director = models.PositiveIntegerField(_('NIP del director'), blank=True, null=True)
    nombre_director = models.CharField(
        _('nombre del director'), max_length=255, blank=True, null=True
    )
    email_director = models.EmailField(_('email del director'), blank=True, null=True)
    unidad_planificacion = models.CharField(
        _('unidad de planificación'), blank=True, max_length=3, null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['academico_id_nk', 'rrhh_id_nk'], name="departamento-unique-academico-rrhh"
            )
        ]

    def __str__(self):
        return f'{self.nombre} ({self.academico_id_nk} / {self.rrhh_id_nk})'


class Estudio(models.Model):
    OPCIONES_RAMA = (
        ('B', _('Formación básica sin rama')),
        ('H', _('Artes y Humanidades')),
        ('J', _('Ciencias Sociales y Jurídicas')),
        ('P', _('Títulos Propios')),
        ('S', _('Ciencias de la Salud')),
        ('T', _('Ingeniería y Arquitectura')),
        ('X', _('Ciencias')),
    )
    id = models.PositiveSmallIntegerField(_('Cód. estudio'), primary_key=True)
    nombre = models.CharField(max_length=255)
    esta_activo = models.BooleanField(_('¿Activo?'), default=True)
    rama = models.CharField(_('rama'), max_length=1, choices=OPCIONES_RAMA)
    tipo_estudio = models.ForeignKey('TipoEstudio', on_delete=models.PROTECT)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.tipo_estudio.nombre})'


class EvaluadorProyecto(models.Model):
    """Asignación de evaluadores a proyectos"""

    evaluador = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, related_name='evaluadores_proyectos'
    )
    proyecto = models.ForeignKey(
        'Proyecto', on_delete=models.PROTECT, related_name='evaluadores_proyectos'
    )
    ha_evaluado = models.BooleanField(_('Ha realizado la evaluación'), null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['evaluador_id', 'proyecto_id'], name="unique-evaluador-proyecto"
            )
        ]


class Evento(models.Model):
    nombre = models.CharField(primary_key=True, max_length=31)


class Licencia(models.Model):
    """Licencia de publicación de la memoria"""

    identificador = models.CharField(
        max_length=255,
        primary_key=True,
        help_text=_('Ver los identificadores estándar en https://spdx.org/licenses/'),
    )
    nombre = models.CharField(max_length=255)
    url = models.URLField('URL', max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} ({self.identificador})'


class Linea(models.Model):
    nombre = models.CharField(max_length=191)
    programa = models.ForeignKey('Programa', on_delete=models.PROTECT, related_name='lineas')

    def __str__(self):
        return f'{self.nombre}'


class Plan(models.Model):
    id_nk = models.PositiveSmallIntegerField(_('Cód. plan'))
    nip_coordinador = models.PositiveIntegerField(_('NIP del coordinador'), blank=True, null=True)
    nombre_coordinador = models.CharField(
        _('nombre del coordinador'), max_length=255, blank=True, null=True
    )
    email_coordinador = models.EmailField(_('email del coordinador'), blank=True, null=True)
    esta_activo = models.BooleanField(_('¿Activo?'), default=True)
    centro = models.ForeignKey('Centro', on_delete=models.PROTECT)
    estudio = models.ForeignKey('Estudio', on_delete=models.PROTECT, related_name='planes')


class ParticipanteProyecto(models.Model):
    proyecto = models.ForeignKey(
        'Proyecto', on_delete=models.PROTECT, related_name='participantes'
    )
    tipo_participacion = models.ForeignKey('TipoParticipacion', on_delete=models.PROTECT)
    usuario = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT, related_name='vinculaciones'
    )

    def get_cargo(self):
        if self.tipo_participacion_id == 'coordinador':
            return _('Coordinadora') if self.usuario.sexo == 'F' else _('Coordinador')
        if self.tipo_participacion_id == 'coordinador_2':
            if self.usuario.sexo == 'F':
                return _('Coordinadora auxiliar')
            return _('Coordinador auxiliar')
        if self.tipo_participacion_id == 'invitacion_rehusada':
            return _('Invitación declinada')
        if self.tipo_participacion_id == 'invitado':
            return ('Invitada') if self.usuario.sexo == 'F' else _('Invitado')
        return _('Participante')


class Programa(models.Model):
    nombre_corto = models.CharField(max_length=15, help_text=_('Ejemplo: PRACUZ'))
    nombre_largo = models.CharField(
        max_length=127, help_text=_('Ejemplo: Programa de Recursos en Abierto para Centros')
    )
    max_ayuda = models.PositiveSmallIntegerField(
        _('Cuantía máxima que se puede solicitar de ayuda'), null=True
    )
    max_estudiantes = models.PositiveSmallIntegerField(
        _('Número máximo de estudiantes por programa'), null=True
    )
    # Para que el coordinador de un proyecto pueda editar un campo,
    # éste debe estar incluido en la tupla `permitidos_coordinador` de views.py.
    campos = models.TextField(null=True)
    convocatoria = models.ForeignKey('Convocatoria', on_delete=models.PROTECT)
    requiere_visto_bueno_centro = models.BooleanField(
        _('¿Requiere el visto bueno del director o decano?'), default='False'
    )
    requiere_visto_bueno_estudio = models.BooleanField(
        _('¿Requiere el visto bueno del coordinador del plan de estudios?'), default='False'
    )

    def __str__(self):
        return f'{self.nombre_corto}'


class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    id_uxxi = models.CharField(
        _('Nº UXXI'),
        max_length=15,
        null=True,
        help_text=_('Número de proyecto asignado en Universitas XXI'),
    )
    codigo = models.CharField(max_length=31, null=True)
    titulo = models.CharField(_('Título'), max_length=255)
    descripcion = models.TextField(
        _('Descripción'),
        null=True,
        max_length=4095,
        help_text=_(
            'Resumen sucinto del proyecto. Máximo recomendable: un párrafo de 10 líneas.<br>'
            'Si copia de Word y se le indica que ha introducido demasiados caracteres, '
            'pruebe a pegar usando Ctrl+Mayúsculas+V.'
        ),
    )
    descripcion_txt = models.TextField(_('Descripción en texto plano'), null=True, max_length=4095)
    estado = models.CharField(
        choices=(
            ('ANULADO', 'Solicitud anulada'),
            ('BORRADOR', 'Solicitud en preparación'),
            ('SOLICITADO', 'Solicitud presentada'),
            ('DENEGADO', 'Denegado por la comisión evaluadora'),
            ('APROBADO', 'Aprobado por la comisión evaluadora'),
            ('RECHAZADO', 'Rechazado por el coordinador'),
            ('ACEPTADO', 'Aceptado por el coordinador'),
            ('MEM_PRESENTADA', 'Memoria presentada'),
            ('MEM_NO_ADMITIDA', 'Memoria no admitida por el corrector'),
            ('MEM_ADMITIDA', 'Memoria admitida por el corrector'),
            ('FINALIZADO_SIN_MEMORIA', 'Finalizado sin memoria'),
        ),
        default='BORRADOR',
        max_length=63,
    )
    # Si se añaden nuevos campos, añadirlos a la tupla `permitidos_coordinador` de views.py
    # si fuera necesario.
    contexto = models.TextField(
        _('Contexto del proyecto'),
        blank=True,
        null=True,
        help_text=_(
            '''Otros proyectos de innovación relacionados con el propuesto, conocimiento que
            se genera y marco epistemológico o teórico que lo avala y descripción del equipo de
            trabajo para la realización del proyecto.'''
        ),
    )
    objetivos = models.TextField(
        _('Objetivos del Proyecto'),
        blank=True,
        null=True,
        help_text=_(
            'Señalando también los relacionados con los Objetivos de Desarrollo Sostenible'
        ),
    )
    metodos_estudio = models.TextField(
        _('Métodos de estudio y trabajo de campo'),
        blank=True,
        null=True,
        help_text=_(
            'Métodos y técnicas utilizadas, características de la muestra, '
            'actividades previstas por los estudiantes y por el equipo del proyecto, '
            'así como calendario de actividades.'
        ),
    )
    mejoras = models.TextField(
        _('Mejoras esperadas en el proceso de enseñanza-aprendizaje y cómo se comprobarán.'),
        blank=True,
        null=True,
        help_text=_('Método de evaluación, resultados e impacto (eficiencia y eficacia)'),
    )
    continuidad = models.TextField(
        _('Continuidad y Expansión'),
        blank=True,
        null=True,
        help_text=_('Transferibilidad, sostenibilidad y difusión prevista'),
    )
    tipo = models.TextField(
        _('Tipo de proyecto'),
        blank=True,
        null=True,
        help_text=_('Experiencia, Estudio o Desarrollo'),
    )
    prauz_titulo = models.CharField(_('Título del curso'), blank=True, null=True, max_length=255)
    prauz_tipo = models.CharField(
        _('Tipo de curso'),
        blank=True,
        null=True,
        # If choices are given, they’re enforced by model validation and the default form widget
        # will be a select box with these choices instead of the standard text field.
        choices=(
            ('Nuevo', _('Nuevo')),
            ('Actualización de otro ya existente', _('Actualización de otro ya existente')),
        ),
        max_length=34,
    )
    prauz_contenido = models.TextField(
        _('Breve descripción del contenido del curso'), blank=True, null=True
    )
    contexto_aplicacion = models.TextField(
        _('Contexto de aplicación/Público objetivo'),
        blank=True,
        null=True,
        help_text=_('Centro, titulación, curso...'),
    )
    metodos = models.TextField(_('Métodos/Técnicas/Actividades utilizadas'), blank=True, null=True)
    tecnologias = models.TextField(_('Tecnologías utilizadas'), blank=True, null=True)
    aplicacion = models.TextField(
        _('Posible aplicación a otros centros/áreas de conocimiento'), blank=True, null=True
    )
    proyectos_anteriores = models.TextField(
        _('Proyectos anteriores'),
        blank=True,
        null=True,
        help_text=_(
            'Nombres de los proyectos de innovación realizados en cursos anteriores '
            'que estén relacionados con la temática propuesta.'
        ),
    )
    impacto = models.TextField(_('Impacto del proyecto'), blank=True, null=True)
    innovacion = models.TextField(_('Tipo de innovación introducida'), blank=True, null=True)
    interes = models.TextField(
        _('Interés y oportunidad para la institución/titulación/centro'), blank=True, null=True
    )
    justificacion_equipo = models.TextField(
        _('Justificación del equipo docente que conforma la solicitud'),
        blank=True,
        null=True,
        help_text=_(
            'Experiencia común conjunta, experiencia previa en el tipo de curso '
            'solicitado, etc.'
        ),
    )
    caracter_estrategico = models.TextField(
        _('Carácter estratégico del curso para la UZ'), blank=True, null=True
    )
    seminario = models.TextField(
        _('Asignatura, curso, seminario o equivalente'), blank=True, null=True
    )
    idioma = models.TextField(
        _('Idioma de publicación'),
        blank=True,
        null=True,
        help_text=_(
            '''Indicar el idioma de publicación y, si además, se publicará la traducción del curso
            completo o parcial a otros idiomas'''
        ),
    )
    ramas = models.CharField(
        _('Rama de conocimiento'),
        blank=True,
        null=True,
        choices=(
            ('Artes y Humanidades', _('Artes y Humanidades')),
            ('Ciencias Sociales y Jurídicas', _('Ciencias Sociales y Jurídicas')),
            ('Ciencias de la Salud', _('Ciencias de la Salud')),
            ('Ingeniería y Arquitectura', _('Ingeniería y Arquitectura')),
            ('Ciencias', _('Ciencias')),
            ('Transversal', _('Transversal')),
        ),
        max_length=767,
    )
    mejoras_pou = models.TextField(
        _('Mejoras esperadas en el Plan de Orientación Universitaria y cómo se comprobarán.'),
        blank=True,
        null=True,
        help_text=_('Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)'),
    )
    ambito = models.TextField(
        _('Ámbito o ámbitos correspondientes a su área de conocimiento'),
        blank=True,
        null=True,
        help_text=_(
            'Consultar las áreas en el bloque derecho de '
            "<a href='https://ocw.unizar.es/ocw/course/index.php?categoryid=8' "
            "target='_blank'>https://ocw.unizar.es/ocw/course/index.php?categoryid=8"
            '</a>.'
        ),
    )
    contenidos = models.TextField(
        _('Breve descripción de los contenidos'),
        blank=True,
        null=True,
        help_text=_(
            'Para OCW indicar los temas, que incluirán teoría, problemas, autoevaluación, etc.'
        ),
    )
    afectadas = models.TextField(
        _('Asignatura/s y Titulación/es afectadas'), blank=True, null=True
    )
    formatos = models.TextField(_('Formatos de los materiales a incluir'), blank=True, null=True)
    # En proyectos anteriores a 2021 el campo `enlace` se usa para recoger la URL de la memoria
    # en la aplicación vieja, para pasarlas a Zaguán vía MarcXML.
    enlace = models.TextField(
        _('Enlace'),
        blank=True,
        null=True,
        help_text=_(
            'Incluir el enlace (o enlaces) a la página de los estudios en la que se '
            'encuentra el plan de mejora y una mención expresa a qué aspecto del mismo '
            'se refiere el proyecto.'
        ),
    )
    contenido_modulos = models.TextField(
        _('Breve descripción de los contenidos de cada capítulo/módulo'),
        blank=True,
        null=True,
        help_text=_(
            'Los cursos 0 deberán incluir un capítulo 0 con las competencias '
            'demandadas al alumnado que va a comenzar el estudio o estudios '
            'objeto del curso.'
        ),
    )
    material_previo = models.TextField(
        _('Indicar si se cuenta con algún material previo'), blank=True, null=True
    )
    duracion = models.TextField(
        _('Duración del curso'),
        blank=True,
        null=True,
        help_text=_(
            'Número de semanas y número de horas de estudio y trabajo autónomo '
            'del participante en todo el curso.'
        ),
    )
    multimedia = models.TextField(
        _('Elementos multimedia e innovadores'),
        blank=True,
        null=True,
        help_text=_(
            '''Descripción específica y cantidad aproximada de los recursos multimedia que incluirá
            el curso en formato video que precisen del uso de un estudio de grabación'''
        ),
    )
    indicadores = models.TextField(
        _('Indicadores para el seguimiento y evaluación del curso'), blank=True, null=True
    )
    actividades = models.TextField(
        _('Actividades de dinamización previstas'),
        blank=True,
        null=True,
        help_text=_('Sólo obligatorias para MOOCs.'),
    )
    financiacion = models.TextField(
        _('Financiación'),
        blank=True,
        null=True,
        help_text=_(
            'Justificar la necesidad de lo solicitado. '
            'Añadir información sobre otras fuentes de financiación.'
        ),
    )
    financiacion_txt = models.TextField(_('Financiación en texto plano'), null=True)
    ayuda = models.PositiveIntegerField(
        _('Ayuda económica solicitada'),
        blank=True,
        null=True,
        help_text=_(
            'Las normas de la convocatoria establecen el importe máximo '
            'que se puede solicitar según el programa.'
        ),
        default=0,
    )
    centro = models.ForeignKey('Centro', on_delete=models.PROTECT, related_name='proyectos')
    convocatoria = models.ForeignKey('Convocatoria', on_delete=models.PROTECT)
    departamento = models.ForeignKey('Departamento', on_delete=models.PROTECT, null=True)
    estudio = models.ForeignKey(
        'Estudio',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        limit_choices_to={'esta_activo': True},
        help_text=_('Sólo obligatorio para PIET.'),
    )
    licencia = models.ForeignKey('Licencia', on_delete=models.PROTECT, null=True)
    linea = models.ForeignKey(
        'Linea',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Línea'),
        help_text=_('En su caso.'),
    )
    programa = models.ForeignKey('Programa', on_delete=models.PROTECT)
    visto_bueno_centro = models.BooleanField(_('Visto bueno del centro'), null=True)
    visto_bueno_estudio = models.BooleanField(_('Visto bueno del plan de estudios'), null=True)
    evaluadores = models.ManyToManyField(
        'accounts.CustomUser', through='EvaluadorProyecto', related_name='proyectos_del_evaluador'
    )
    esta_evaluado = models.BooleanField(_('Ha sido evaluado'), null=True)
    # Aprobación de la Comisión Evaluadora
    aceptacion_comision = models.BooleanField(_('Aprobación por la comisión'), null=True)
    ayuda_provisional = models.PositiveIntegerField(
        _('Ayuda económica concedida (provisional)'), null=True
    )
    ayuda_definitiva = models.PositiveIntegerField(
        _('Ayuda económica concedida (definitiva)'), null=True, blank=True
    )
    tipo_gasto = models.TextField(
        _('Tipo de gasto posible'),
        help_text=_('Indicar los gastos autorizados indicados por la Comisión.'),
        null=True,
    )
    puntuacion = models.DecimalField(
        verbose_name=_('Puntuación obtenida'), max_digits=3, decimal_places=1, null=True
    )
    observaciones = models.TextField(_('Observaciones internas'), null=True)
    # Aceptación por el coordinador de las condiciones decididas por la Comisión
    aceptacion_coordinador = models.BooleanField(_('Aceptación por el coordinador'), null=True)
    # Corrector/consultor de las memorias
    corrector = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        on_delete=models.PROTECT,
        related_name='proyectos_corregidos',
    )
    aceptacion_corrector = models.BooleanField(_('Admisión por el corrector'), null=True)
    es_publicable = models.BooleanField(_('¿Publicar la memoria?'), null=True)
    observaciones_corrector = models.TextField(
        _('Observaciones del corrector de la memoria'), null=True
    )
    aceptacion_economico = models.BooleanField(_('Cierre económico'), default=False)

    class Meta:
        permissions = [
            ('listar_proyectos', _('Puede ver el listado de todos los proyectos.')),
            ('ver_proyecto', _('Puede ver cualquier proyecto.')),
            ('editar_proyecto', _('Puede editar cualquier proyecto en cualquier momento.')),
            ('listar_evaluaciones', _('Puede ver el listado de evaluaciones de los proyectos.')),
            ('listar_evaluadores', _('Puede ver el listado de evaluadores.')),
            ('editar_evaluadores', _('Puede editar los evaluadores de un proyecto.')),
            ('editar_resolucion', _('Puede modificar la resolución de la Comisión Evaluadora.')),
            ('listar_correctores', _('Puede ver el listado de correctores.')),
            ('editar_corrector', _('Puede modificar el corrector de un proyecto.')),
            ('ver_evaluacion', _('Puede ver la evaluación de cualquier proyecto.')),
            ('ver_memorias', _('Puede ver el listado y cualquier memoria de proyecto.')),
            ('ver_resolucion', _('Puede ver las resoluciones de la Comisión Evaluadora.')),
            ('ver_up', _('Puede ver el listado de UP y gastos de los proyectos.')),
            ('ver_economico', _('Puede ver/editar el cierre económico de los proyectos.')),
            ('zaguan', _('Puede enviar memorias al repositorio institucional.')),
        ]

    def __str__(self):
        return self.codigo

    def get_absolute_url(self):
        return reverse('proyecto_detail', args=[str(self.id)])

    def en_borrador(self):
        return self.estado == 'BORRADOR'

    def get_pp_coordinador_or_none(self, tipo) -> ParticipanteProyecto | None:
        """Busca el coordinador o coordinador_2 del proyecto"""
        try:
            return self.participantes.get(tipo_participacion_id=tipo)
        except ParticipanteProyecto.DoesNotExist:
            return None

    @classmethod
    def get_todos(cls, anyo):
        """Devuelve datos de todos los proyectos introducidos en el año indicado."""

        cabeceras = [
            _('Programa'),
            _('Línea'),
            _('ID'),
            _('Título'),
            _('Nombre coordinador'),
            _('Apellido 1 coordinador'),
            _('Apellido 1 coordinador'),
            _('NIP Coordinador'),
            _('Correo coordinador'),
            _('Estado'),
            _('VºBº C'),
            _('VºBº E'),
            _('Núm. participantes'),
            _('Evaluadores'),
            _('Correo evaluadores'),
            _('Está evaluado'),
            _('Ayuda solicitada'),
            _('Resolución'),
            _('Ayuda provisional'),
            _('Ayuda definitiva'),
            _('Aceptación coordinador'),
        ]

        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                SELECT prog.nombre_corto AS 'programa', l.nombre AS 'línea',
                    p.id, p.titulo,
                    u1.first_name AS 'nombre coordinador',
                    u1.last_name AS 'apellido 1 coord',
                    u1.last_name_2 AS 'apellido 2 coord',
                    u1.username AS 'nip coord',
                    u1.email AS 'correo coord',
                    p.estado,
                    CASE p.visto_bueno_centro
                      WHEN 1 THEN 'S'
                      WHEN 0 THEN 'N'
                      ELSE '-'
                    END AS 'VºBº Centro',
                    CASE p.visto_bueno_estudio
                      WHEN 1 THEN 'S'
                      WHEN 0 THEN 'N'
                      ELSE '-'
                    END AS 'VºBº Estudio',
                    COUNT(pp2.id) AS 'núm. participantes',
                    GROUP_CONCAT(
                        DISTINCT CONCAT_WS(' ', u2.first_name, u2.last_name, u2.last_name_2
                    ) ORDER BY u2.id) AS evaluadores,
                    GROUP_CONCAT(DISTINCT u2.email ORDER BY u2.id),
                    CASE p.esta_evaluado
                      WHEN 1 THEN 'S'
                      WHEN 0 THEN 'N'
                      ELSE '-'
                    END AS 'está evaluado',
                    p.ayuda AS 'ayuda solicitada',
                    CASE p.aceptacion_comision
                      WHEN 1 THEN 'S'
                      WHEN 0 THEN 'N'
                      ELSE '-'
                    END AS 'aceptación comisión',
                    p.ayuda_provisional,
                    p.ayuda_definitiva,
                    CASE p.aceptacion_coordinador
                      WHEN 1 THEN 'S'
                      WHEN 0 THEN 'N'
                      ELSE '-'
                    END AS 'aceptación coordinador'
                FROM indo_proyecto p
                JOIN indo_programa prog ON p.programa_id = prog.id
                LEFT JOIN indo_linea l ON p.linea_id = l.id
                JOIN indo_participanteproyecto pp
                  ON p.id = pp.proyecto_id AND pp.tipo_participacion_id = 'coordinador'
                JOIN accounts_customuser u1 ON pp.usuario_id = u1.id
                LEFT JOIN indo_participanteproyecto pp2
                       ON p.id = pp2.proyecto_id AND pp2.tipo_participacion_id = 'participante'
                LEFT JOIN indo_evaluadorproyecto ep ON p.id = ep.proyecto_id
                LEFT JOIN accounts_customuser u2 ON ep.evaluador_id = u2.id
                WHERE prog.convocatoria_id = {anyo}
                GROUP BY prog.nombre_corto, l.nombre, p.id, p.titulo,
                         u1.first_name, u1.last_name, u1.last_name_2, u1.username, u1.email,
                         p.estado, p.visto_bueno_centro, p.visto_bueno_estudio,
                         p.esta_evaluado, p.ayuda, p.aceptacion_comision,
                         p.ayuda_provisional, p.ayuda_definitiva, p.aceptacion_coordinador
                ORDER BY p.programa_id, p.linea_id, p.titulo;
                '''
            )
            rows = cursor.fetchall()

        datos_proyectos = list(rows)
        datos_proyectos.insert(0, cabeceras)
        return datos_proyectos

    @classmethod
    def get_up_gastos(cls, anyo):
        """Devuelve datos de las UP y gastos posibles de todos los proyectos del año indicado."""
        cabeceras = [
            _('Programa'),
            _('ID'),
            _('Título'),
            _('Coordinador'),
            _('UP'),
            _('Ayuda definitiva'),
            _('Tipo de gasto posible'),
            _('Nº UXXI'),
        ]
        proyectos = (
            Proyecto.objects.filter(convocatoria__id=anyo)
            .filter(aceptacion_coordinador=True)
            .order_by('programa__nombre_corto', 'titulo')
        )
        datos_proyectos = [
            [
                p.programa,
                p.id,
                p.titulo,
                p.coordinador.full_name,
                p.get_unidad_planificacion(),
                p.ayuda_definitiva,
                p.tipo_gasto,
                p.id_uxxi,
            ]
            for p in proyectos
        ]
        datos_proyectos.insert(0, cabeceras)
        return datos_proyectos

    def get_unidad_planificacion(self) -> str | None:
        """Devuelve el ID de la Unidad de Planificación del proyecto

        PIEC, PIPOUZ, PIET: UP del centro del proyecto
        PIIDUZ, PRAUZ, MOOC, PISOC: UP del departamento del coordinador del proyecto
        """
        if self.programa.nombre_corto in ('PIEC', 'PIPOUZ', 'PIET'):
            return f'{self.centro.unidad_planificacion} ({self.centro.nombre})'
        elif self.programa.nombre_corto in ('PIIDUZ', 'PRAUZ', 'MOOC', 'PISOC'):
            return (
                f'{self.coordinador.departamentos[0].unidad_planificacion}'
                + f' ({self.coordinador.departamentos[0].nombre})'
                if self.coordinador.departamentos
                else None
            )
        return None

    @property
    def coordinador(self):
        """Devuelve el usuario coordinador del proyecto"""
        pp_coordinador = self.get_pp_coordinador_or_none('coordinador')
        return pp_coordinador.usuario if pp_coordinador else None

    @property
    def coordinador_2(self):
        """Devuelve el segundo coordinador del proyecto (los PIET podían tener 2)."""
        pp_coordinador_2 = self.get_pp_coordinador_or_none('coordinador_2')
        return pp_coordinador_2.usuario if pp_coordinador_2 else None

    def get_coordinadores(self):
        """Devuelve los usuarios coordinadores del proyecto."""
        coordinadores = [self.coordinador, self.coordinador_2]
        return list(filter(None, coordinadores))

    def get_dict_valoraciones(self, user_id: int) -> dict[int, Valoracion]:
        """Devuelve diccionario criterio_id => valoración con las valoraciones de un evaluador."""
        return {
            valoracion.criterio_id: valoracion
            for valoracion in self.valoraciones.filter(evaluador__id=user_id).all()
        }

    def get_dict_respuestas_memoria(self):
        """Devuelve un diccionario subapartado_id => respuesta de la memoria del proyecto."""
        return {respuesta.subapartado_id: respuesta for respuesta in self.respuestas_memoria.all()}

    @property
    def usuarios_participantes(self):
        """Devuelve una lista de los usuarios participantes en el proyecto."""
        participantes_proyecto = (
            self.participantes.filter(tipo_participacion='participante')
            .order_by('usuario__first_name', 'usuario__last_name')
            .all()
        )
        return [pp.usuario for pp in participantes_proyecto]

    def get_usuarios_vinculados(self):
        """
        Devuelve todos los usuarios vinculados al proyecto
        (invitados, participantes, etc).
        """
        return list(map(lambda p: p.usuario, self.participantes.all()))

    @property
    def numero_participantes(self):
        """Devuelve la cantidad de partipantes que han aceptado la invitación."""
        return self.participantes.filter(tipo_participacion='participante').count()

    def tiene_invitados(self):
        """Devuelve si el proyecto tiene al menos un invitado."""
        num_invitados = self.participantes.filter(tipo_participacion='invitado').count()
        return num_invitados >= 1

    def tiene_participantes(self):
        """Devuelve si el proyecto tiene algún participante que haya aceptado la invitación."""
        return self.numero_participantes >= 1


class MemoriaApartado(models.Model):
    """Apartados de la memoria"""

    convocatoria = models.ForeignKey(
        'Convocatoria', on_delete=models.PROTECT, related_name='apartados_memoria'
    )
    numero = models.PositiveSmallIntegerField(_('número'))
    descripcion = models.CharField(_('descripción'), max_length=255)

    class Meta:
        ordering = ('convocatoria__id', 'numero')
        verbose_name = _('apartado de la memoria')
        verbose_name_plural = _('apartados de la memoria')

    def __str__(self):
        return self.descripcion


class MemoriaSubapartado(models.Model):
    """Subapartados de la memoria"""

    class Tipo(models.TextChoices):
        """Tipo de subapartado.

        Los subapartados pueden ser de dos tipos:

        * Texto libre - El coordinador puede introducir un texto con sus comentarios.
        * Fichero - El coordinador puede adjuntar un fichero PDF.
        """

        TEXTO = 'texto', _('Texto libre')
        FICHERO = 'fichero', _('Fichero')

    apartado = models.ForeignKey(
        'MemoriaApartado', on_delete=models.PROTECT, related_name='subapartados'
    )
    peso = models.PositiveSmallIntegerField(_('peso'))
    descripcion = models.CharField(_('descripción'), max_length=255)
    ayuda = models.CharField(_('texto de ayuda'), max_length=255)
    tipo = models.CharField(_('tipo'), max_length=15, choices=Tipo.choices)

    class Meta:
        ordering = ('apartado__numero', 'peso')
        verbose_name = _('subapartado de la memoria')
        verbose_name_plural = _('subapartados de la memoria')

    def __str__(self):
        return self.descripcion

    @property
    def numero_apartado(self):
        return self.apartado.numero


class MemoriaRespuesta(models.Model):
    """Respuestas a los subapartados de la memoria"""

    proyecto = models.ForeignKey(
        'Proyecto', on_delete=models.PROTECT, related_name='respuestas_memoria'
    )
    subapartado = models.ForeignKey(
        'MemoriaSubapartado', on_delete=models.PROTECT, related_name='respuestas'
    )
    texto = models.TextField(_('texto'), blank=True, null=True)
    fichero = models.FileField(
        'fichero PDF',
        upload_to='anexos_memoria/%Y/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

    class Meta:
        ordering = ('-proyecto__id', 'subapartado')
        constraints = [
            models.UniqueConstraint(
                fields=['proyecto_id', 'subapartado_id'], name="unique-proyecto-subapartado"
            )
        ]
        verbose_name = _('respuesta de la memoria')
        verbose_name_plural = _('respuestas de la memoria')

    def __str__(self):
        return self.texto

    @classmethod
    def get_or_create(cls, proyecto_id, subapartado_id):
        """Devuelve la respuesta al supapartado de la memoria y proyecto indicados."""
        try:
            respuesta = MemoriaRespuesta.objects.get(
                proyecto_id=proyecto_id, subapartado_id=subapartado_id
            )
        except MemoriaRespuesta.DoesNotExist:
            respuesta = MemoriaRespuesta.objects.create(
                proyecto_id=proyecto_id, subapartado_id=subapartado_id
            )
        return respuesta


class Opcion(models.Model):
    """Respuestas posibles a los criterios, cada una con una puntuación."""

    criterio = models.ForeignKey('Criterio', on_delete=models.PROTECT, related_name='opciones')
    puntuacion = models.PositiveSmallIntegerField(_('puntuación'))
    descripcion = models.CharField(_('descripción'), max_length=255)

    class Meta:
        ordering = ('criterio__parte', 'criterio__peso', 'puntuacion')
        verbose_name = _('opción')
        verbose_name_plural = _('opciones')

    def __str__(self):
        return self.descripcion


class Registro(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    evento = models.ForeignKey('Evento', on_delete=models.PROTECT)
    proyecto = models.ForeignKey('Proyecto', on_delete=models.PROTECT)
    usuario = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.PROTECT, related_name='registros'
    )
    ip_address = models.GenericIPAddressField(_('Dirección IP'), null=True)


class Resolucion(models.Model):
    """Datos sobre una resolución publicada en el tablón de anuncios."""

    fecha = models.DateField(default=datetime.date.today)
    titulo = models.CharField(_('título'), max_length=255)
    url = models.URLField(
        'URL',
        help_text=_(
            'Dirección de la página web. '
            'Vg: https://ae.unizar.es/?app=touz&opcion=mostrar&id=12345'
        ),
        max_length=255,
    )

    class Meta:
        ordering = ('fecha',)
        verbose_name = _('resolución')
        verbose_name_plural = _('resoluciones')


class RightsSupport(models.Model):
    """Dummy auxiliary model in order to create global permissions not related to a model."""

    class Meta:
        # No database table creation or deletion operations will be performed for this model.
        managed = False

        permissions = (
            ('gestionar_correctores', _('Puede añadir/quitar usuarios al grupo Correctores')),
            ('asignar_correctores', _('Puede asignar un corrector de memoria a un proyecto')),
            ('hace_constar', _('Puede generar PDFs de constancia de participación en proyectos')),
        )


class TipoEstudio(models.Model):
    id = models.PositiveSmallIntegerField(_('Cód. tipo estudio'), primary_key=True)
    nombre = models.CharField(max_length=63)


class TipoParticipacion(models.Model):
    nombre = models.CharField(primary_key=True, max_length=63)


class Valoracion(models.Model):
    """Valoración de un proyecto, atendiendo a los criterios establecidos en la convocatoria."""

    proyecto = models.ForeignKey('Proyecto', on_delete=models.PROTECT, related_name='valoraciones')
    criterio = models.ForeignKey('Criterio', on_delete=models.PROTECT)
    opcion = models.ForeignKey('Opcion', null=True, on_delete=models.PROTECT)
    texto = models.TextField(_('texto'), blank=True, null=True)
    evaluador = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.PROTECT, related_name='valoraciones'
    )

    class Meta:
        verbose_name = _('valoración')
        verbose_name_plural = _('valoraciones')

    @classmethod
    def get_todas(cls, anyo):
        """Devuelve las valoraciones de todos los proyectos aceptados en el año indicado."""
        cabeceras = [
            _('Programa'),
            _('Línea'),
            _('ID'),
            _('Título'),
            _('Centro'),
            _('Ayuda solicitada'),
            _('Financiación'),
        ]
        criterios = Criterio.objects.filter(convocatoria_id=anyo).order_by('parte', 'peso').all()
        cabeceras.extend([criterio.descripcion for criterio in criterios])

        with connection.cursor() as cursor:
            # Columnas procedentes de la solicitud de proyecto
            cursor.execute(
                f'''
                SELECT prog.nombre_corto, l.nombre,
                  p.id, p.titulo, c.nombre, p.ayuda, p.financiacion_txt
                FROM indo_evaluadorproyecto ep
                JOIN indo_proyecto p ON ep.proyecto_id = p.id
                JOIN indo_programa prog ON p.programa_id = prog.id
                LEFT JOIN indo_linea l ON p.linea_id = l.id
                LEFT JOIN indo_centro c ON p.centro_id = c.id
                WHERE prog.convocatoria_id = {anyo}
                ORDER BY ep.proyecto_id, ep.evaluador_id;
                '''
            )
            rows = cursor.fetchall()
            # Podríamos añadir las columnas de la evaluación a este array bidimensional
            #   usando NumPy o bucles.
            # En su lugar, transponemos la matriz, y las añadiremos como filas.
            # A continuación, volveremos a transponer la matriz.
            valoraciones = list(zip(*rows))

            # Columnas procedentes de la evaluación del proyecto
            for criterio in criterios:
                cursor.execute(
                    f'''
                    SELECT CASE
                      WHEN c.tipo = 'opcion' THEN o.puntuacion
                      WHEN c.tipo = 'texto' THEN v.texto
                      ELSE NULL
                    END AS valoracion
                    FROM indo_evaluadorproyecto ep
                    JOIN indo_proyecto p ON ep.proyecto_id = p.id
                    JOIN indo_programa prog ON p.programa_id = prog.id
                    LEFT JOIN indo_valoracion v
                           ON ep.proyecto_id = v.proyecto_id AND ep.evaluador_id=v.evaluador_id
                    LEFT JOIN indo_criterio c ON v.criterio_id = c.id
                    LEFT JOIN indo_opcion o ON v.opcion_id = o.id
                    WHERE prog.convocatoria_id = {anyo}
                      AND (v.criterio_id = {criterio.id} OR v.criterio_id IS NULL)
                    ORDER BY ep.proyecto_id, ep.evaluador_id, c.parte, c.peso;
                    '''
                )
                rows = cursor.fetchall()
                fila_del_criterio = [row[0] for row in rows]
                valoraciones.append(fila_del_criterio)

        valoraciones = list(zip(*valoraciones))

        valoraciones.insert(0, cabeceras)
        return valoraciones
