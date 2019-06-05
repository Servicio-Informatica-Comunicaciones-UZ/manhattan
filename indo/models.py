from datetime import date
from django.db import models
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Centro(models.Model):
    id = models.IntegerField(primary_key=True)
    academico_id_nk = models.IntegerField(_("cód. académico"), blank=True, null=True)
    rrhh_id_nk = models.CharField(
        _("cód. RRHH"), max_length=4, blank=True, null=True, unique=True
    )
    nombre = models.CharField(max_length=255)
    tipo_centro = models.CharField(
        _("tipo de centro"), max_length=30, blank=True, null=True
    )
    direccion = models.CharField(_("dirección"), max_length=140, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(_("teléfono"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    url = models.URLField("URL", max_length=255, blank=True, null=True)
    nip_decano = models.PositiveIntegerField(
        _("NIP del decano o director"), blank=True, null=True
    )
    nombre_decano = models.CharField(
        _("nombre del decano o director"), max_length=255, blank=True, null=True
    )
    email_decano = models.EmailField(
        _("email del decano o director"), blank=True, null=True
    )
    tratamiento_decano = models.CharField(
        _("cargo"),
        max_length=25,
        blank=True,
        null=True,
        help_text=_("Decano/a ó director(a)."),
    )
    nip_secretario = models.PositiveIntegerField(
        _("NIP del secretario"), blank=True, null=True
    )
    nombre_secretario = models.CharField(
        _("nombre del secretario"), max_length=255, blank=True, null=True
    )
    email_secretario = models.EmailField(
        _("email del secretario"), blank=True, null=True
    )
    nips_coord_pou = models.CharField(
        _("NIPs de los coordinadores POU"), blank=True, max_length=255, null=True
    )
    nombres_coords_pou = models.CharField(
        _("nombres de los coordinadores POU"), blank=True, max_length=1023, null=True
    )
    emails_coords_pou = models.CharField(
        _("emails de los coordinadores POU"), blank=True, max_length=1023, null=True
    )
    unidad_gasto = models.CharField(
        _("unidad de gasto"), blank=True, max_length=3, null=True
    )
    esta_activo = models.BooleanField(_("¿Activo?"), default=False)

    def __str__(self):
        return f"{self.academico_id_nk} {self.rrhh_id_nk} {self.nombre}"

    class Meta:
        indexes = [models.Index(fields=["academico_id_nk"])]


class Convocatoria(models.Model):
    id = models.PositiveSmallIntegerField(_("año"), primary_key=True)
    fecha_min_solicitudes = models.DateField()
    fecha_max_solicitudes = models.DateField()
    fecha_max_aceptos = models.DateField()
    fecha_max_visto_buenos = models.DateField()

    def __str__(self):
        return str(self.id)


class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)
    academico_id_nk = models.IntegerField(
        "cód. académico", blank=True, db_index=True, null=True
    )
    rrhh_id_nk = models.CharField(
        "cód. RRHH", max_length=4, blank=True, null=True, unique=True
    )
    nombre = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(_("email del departamento"), blank=True, null=True)
    email_secretaria = models.EmailField(
        _("email de la secretaría"), blank=True, null=True
    )
    nip_director = models.PositiveIntegerField(
        _("NIP del director"), blank=True, null=True
    )
    nombre_director = models.CharField(
        _("nombre del director"), max_length=255, blank=True, null=True
    )
    email_director = models.EmailField(_("email del director"), blank=True, null=True)
    unidad_gasto = models.CharField(
        _("unidad de gasto"), blank=True, max_length=3, null=True
    )

    def __str__(self):
        return f"{self.academico_id_nk} {self.rrhh_id_nk} {self.nombre}"


class Estudio(models.Model):
    OPCIONES_RAMA = (
        ("B", "Formación básica sin rama"),
        ("H", "Artes y Humanidades"),
        ("J", "Ciencias Sociales y Jurídicas"),
        ("P", "Títulos Propios"),
        ("S", "Ciencias de la Salud"),
        ("T", "Ingeniería y Arquitectura"),
        ("X", "Ciencias"),
    )
    id = models.PositiveSmallIntegerField(_("Cód. estudio"), primary_key=True)
    nombre = models.CharField(max_length=255)
    esta_activo = models.BooleanField("¿Activo?", default=True)
    rama = models.CharField(max_length=1, choices=OPCIONES_RAMA)
    tipo_estudio = models.ForeignKey("TipoEstudio", on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    nombre = models.CharField(primary_key=True, max_length=31)


class Licencia(models.Model):
    """Licencia de publicación de la memoria"""

    identificador = models.CharField(
        max_length=255,
        primary_key=True,
        help_text=_("Ver los identificadores estándar en https://spdx.org/licenses/"),
    )
    nombre = models.CharField(max_length=255)
    url = models.URLField("URL", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.identificador})"


class Linea(models.Model):
    nombre = models.CharField(max_length=31)
    programa = models.ForeignKey(
        "Programa", on_delete=models.PROTECT, related_name="lineas"
    )

    def __str__(self):
        return f"{self.nombre}"


class Plan(models.Model):
    id_nk = models.PositiveSmallIntegerField(_("Cód. plan"))
    nip_coordinador = models.PositiveIntegerField(
        _("NIP del coordinador"), blank=True, null=True
    )
    nombre_coordinador = models.CharField(
        _("nombre del coordinador"), max_length=255, blank=True, null=True
    )
    email_coordinador = models.EmailField(
        _("email del coordinador"), blank=True, null=True
    )
    esta_activo = models.BooleanField(_("¿Activo?"), default=True)
    centro = models.ForeignKey("Centro", on_delete=models.PROTECT)
    estudio = models.ForeignKey("Estudio", on_delete=models.PROTECT)


class ParticipanteProyecto(models.Model):
    proyecto = models.ForeignKey(
        "Proyecto", on_delete=models.PROTECT, related_name="participantes"
    )
    tipo_participacion = models.ForeignKey(
        "TipoParticipacion", on_delete=models.PROTECT
    )
    usuario = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)

    def get_cargo(self):
        if self.tipo_participacion.nombre == "coordinador":
            return _("Coordinadora") if self.usuario.sexo == "F" else _("Coordinador")
        if self.tipo_participacion.nombre == "coordinador_principal":
            if self.usuario.sexo == "F":
                return _("Coordinadora principal")
            return _("Coordinador principal")
        return _("Participante")


class Programa(models.Model):
    nombre_corto = models.CharField(max_length=15, help_text=_("Ejemplo: PRACUZ"))
    nombre_largo = models.CharField(
        max_length=127,
        help_text=_("Ejemplo: Programa de Recursos en Abierto para Centros"),
    )
    max_ayuda = models.PositiveSmallIntegerField(
        _("Cuantía máxima que se puede solicitar de ayuda"), null=True
    )
    max_estudiantes = models.PositiveSmallIntegerField(
        _("Número máximo de estudiantes por programa"), null=True
    )
    campos = models.TextField(null=True)
    convocatoria = models.ForeignKey("Convocatoria", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre_corto}"


class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=31, null=True)
    titulo = models.CharField(_("Título"), max_length=255)
    descripcion = models.TextField(
        _("Descripción"),
        null=True,
        max_length=4095,
        help_text=_(
            "Resumen sucinto del proyecto. Máximo recomendable: "
            "un párrafo de 10 líneas."
        ),
    )
    estado = models.CharField(
        choices=(
            ("BORRADOR", "Solicitud en preparación"),
            ("SOLICITADO", "Solicitud presentada"),
        ),
        default="BORRADOR",
        max_length=63,
    )
    contexto = models.TextField(
        _("Contexto del proyecto"),
        blank=True,
        null=True,
        help_text=_(
            "Necesidad a la que responde el proyecto, mejoras esperadas respecto "
            "al estado de la cuestión, conocimiento que se genera."
        ),
    )
    objetivos = models.TextField(_("Objetivos del Proyecto"), blank=True, null=True)
    metodos_estudio = models.TextField(
        _("Métodos de estudio/experimentación y trabajo de campo"),
        blank=True,
        null=True,
        help_text=_(
            "Métodos/técnicas utilizadas, características de la muestra, "
            "actividades previstas por los estudiantes y por el equipo del proyecto, "
            "calendario de actividades."
        ),
    )
    mejoras = models.TextField(
        _(
            "Mejoras esperadas en el proceso de enseñanza-aprendizaje "
            "y cómo se comprobarán."
        ),
        blank=True,
        null=True,
        help_text=_(
            "Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)"
        ),
    )
    continuidad = models.TextField(
        _("Continuidad y Expansión"),
        blank=True,
        null=True,
        help_text=_("Transferibilidad, Sostenibilidad, Difusión prevista"),
    )
    tipo = models.TextField(
        _("Tipo de proyecto"),
        blank=True,
        null=True,
        help_text=_("Experiencia, Estudio o Desarrollo"),
    )
    contexto_aplicacion = models.TextField(
        _("Contexto de aplicación/Público objetivo"),
        blank=True,
        null=True,
        help_text=_("Centro, titulación, curso..."),
    )
    metodos = models.TextField(
        _("Métodos/Técnicas/Actividades utilizadas"), blank=True, null=True
    )
    tecnologias = models.TextField(_("Tecnologías utilizadas"), blank=True, null=True)
    aplicacion = models.TextField(
        _("Posible aplicación a otros centros/áreas de conocimiento"),
        blank=True,
        null=True,
    )
    proyectos_anteriores = models.TextField(
        _("Proyectos anteriores"),
        blank=True,
        null=True,
        help_text=_(
            "Nombres de los proyectos de innovación realizados en cursos anteriores "
            "que estén relacionados con la temática propuesta."
        ),
    )
    impacto = models.TextField(_("Impacto del proyecto"), blank=True, null=True)
    innovacion = models.TextField(
        _("Tipo de innovación introducida"), blank=True, null=True
    )
    interes = models.TextField(
        _("Interés y oportunidad para la institución/titulación/centro"),
        blank=True,
        null=True,
    )
    justificacion_equipo = models.TextField(
        _("Justificación del equipo docente que conforma la solicitud"),
        blank=True,
        null=True,
        help_text=_(
            "Experiencia común conjunta, experiencia previa en el tipo de curso "
            "solicitado, etc."
        ),
    )
    caracter_estrategico = models.TextField(
        _("Carácter estratégico del curso para la UZ"), blank=True, null=True
    )
    seminario = models.TextField(
        _("Asignatura, curso, seminario o equivalente"), blank=True, null=True
    )
    idioma = models.TextField(_("Idioma de publicación"), blank=True, null=True)
    ramas = models.TextField(_("Ramas de conocimiento"), blank=True, null=True)
    mejoras_pou = models.TextField(
        _(
            "Mejoras esperadas en el Plan de Orientación Universitaria "
            "y cómo se comprobarán."
        ),
        blank=True,
        null=True,
        help_text=_(
            "Método de evaluación, Resultados, Impacto (Eficiencia y Eficacia)"
        ),
    )
    ambito = models.TextField(
        _("Ámbito o ámbitos correspondientes a su área de conocimiento"),
        blank=True,
        null=True,
        help_text=_(
            "Consultar las áreas en el bloque derecho de "
            "<a href='https://ocw.unizar.es/ocw/course/index.php?categoryid=8' "
            "target='_blank'>https://ocw.unizar.es/ocw/course/index.php?categoryid=8"
            "</a>."
        ),
    )
    contenidos = models.TextField(
        _("Breve descripción de los contenidos"),
        blank=True,
        null=True,
        help_text=_(
            "Para OCW indicar los temas, que incluirán teoría, problemas, "
            "autoevaluación, etc."
        ),
    )
    afectadas = models.TextField(
        _("Asignatura/s y Titulación/es afectadas"), blank=True, null=True
    )
    formatos = models.TextField(
        _("Formatos de los materiales incluidos."), blank=True, null=True
    )
    enlace = models.TextField(
        _("Enlace"),
        blank=True,
        null=True,
        help_text=_(
            "Incluir el enlace (o enlaces) a la página de los estudios en la que se "
            "encuentra el plan de mejora y una mención expresa a qué aspecto del mismo "
            "se refiere el proyecto."
        ),
    )
    contenido_modulos = models.TextField(
        _("Breve descripción de los contenidos de cada capítulo/módulo"),
        blank=True,
        null=True,
        help_text=_(
            "Los cursos 0 deberán incluir un capítulo 0 con las competencias "
            "demandadas al alumnado que va a comenzar el estudio o estudios "
            "objeto del curso."
        ),
    )
    material_previo = models.TextField(
        _("Indicar si se cuenta con algún material previo"), blank=True, null=True
    )
    duracion = models.TextField(
        _("Duración del curso"),
        blank=True,
        null=True,
        help_text=_(
            "Número de semanas y número de horas de estudio y trabajo autónomo "
            "del participante en todo el curso."
        ),
    )
    multimedia = models.TextField(
        _("Elementos multimedia e innovadores"),
        blank=True,
        null=True,
        help_text=_(
            "Elementos multimedia e innovadores que va a utilizar "
            "en la elaboración del curso."
        ),
    )
    indicadores = models.TextField(
        _("Indicadores para el seguimiento y evaluación del curso"),
        blank=True,
        null=True,
    )
    actividades = models.TextField(
        _("Actividades de dinamización previstas"),
        blank=True,
        null=True,
        help_text=_("Sólo obligatorias para MOOCs."),
    )
    financiacion = models.TextField(
        _("Financiación"),
        blank=True,
        null=True,
        help_text=_(
            "Justificar la necesidad de lo solicitado. "
            "Añadir información sobre otras fuentes de financiación."
        ),
    )
    ayuda = models.PositiveIntegerField(
        _("Ayuda económica solicitada"),
        blank=True,
        null=True,
        help_text=_(
            "Las normas de la convocatoria establecen el importe máximo "
            "que se puede solicitar según el programa."
        ),
        default=0,
    )
    centro = models.ForeignKey(
        "Centro",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Sólo obligatorio para PIEC, PRACUZ, PIPOUZ."),
    )
    convocatoria = models.ForeignKey("Convocatoria", on_delete=models.PROTECT)
    departamento = models.ForeignKey(
        "Departamento", on_delete=models.PROTECT, null=True
    )
    estudio = models.ForeignKey(
        "Estudio",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Sólo obligatorio para PIET."),
    )
    licencia = models.ForeignKey("Licencia", on_delete=models.PROTECT, null=True)
    linea = models.ForeignKey(
        "Linea",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        limit_choices_to=Q(programa__convocatoria_id=date.today().year),
        verbose_name=_("Línea"),
        help_text=_("En su caso."),
    )
    programa = models.ForeignKey(
        "Programa",
        on_delete=models.PROTECT,
        limit_choices_to={"convocatoria_id": date.today().year},
    )

    def en_borrador(self):
        return self.estado == "BORRADOR"

    def get_absolute_url(self):
        return reverse("proyecto_detail", args=[str(self.id)])

    def get_participante_or_none(self, tipo):
        try:
            return ParticipanteProyecto.objects.get(
                proyecto_id=self.id, tipo_participacion_id=tipo
            )
        except ParticipanteProyecto.DoesNotExist:
            return None

    def get_usuario_coordinador(self):
        pp = ParticipanteProyecto.objects.get(
            proyecto_id=self.id, tipo_participacion_id="coordinador"
        )
        return pp.usuario

    def get_usuarios_vinculados(self):
        """
        Devuelve todos los usuarios vinculados al proyecto
        (invitados, participantes, etc).
        """
        return list(map(lambda p: p.usuario, self.participantes.all()))

    def tiene_invitados(self):
        """Devuelve si el proyecto tiene al menos un invitado."""
        num_invitados = self.participantes.filter(tipo_participacion="invitado").count()
        return num_invitados >= 1

    def __str__(self):
        return self.codigo


class Registro(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    evento = models.ForeignKey("Evento", on_delete=models.PROTECT)
    proyecto = models.ForeignKey("Proyecto", on_delete=models.PROTECT)


class TipoEstudio(models.Model):
    id = models.PositiveSmallIntegerField(_("Cód. tipo estudio"), primary_key=True)
    nombre = models.CharField(max_length=63)


class TipoParticipacion(models.Model):
    nombre = models.CharField(primary_key=True, max_length=63)
