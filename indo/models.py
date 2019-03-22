from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Centro(models.Model):
    id = models.IntegerField(primary_key=True)
    academico_id_nk = models.IntegerField("cód. académico", blank=True, null=True)
    rrhh_id_nk = models.CharField(
        "cód. RRHH", max_length=4, blank=True, null=True, unique=True
    )
    nombre = models.CharField(max_length=255)
    tipo_centro = models.CharField(
        "tipo de centro", max_length=30, blank=True, null=True
    )
    direccion = models.CharField("dirección", max_length=140, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField("teléfono", max_length=30, blank=True, null=True)
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
    nip_coord_pou = models.PositiveIntegerField(
        _("NIP del coordinador POU"), blank=True, null=True
    )
    nombre_coord_pou = models.CharField(
        _("nombre del coordinador POU"), max_length=255, blank=True, null=True
    )
    email_coord_pou = models.EmailField(
        _("email del coordinador POU"), blank=True, null=True
    )
    esta_activo = models.BooleanField("¿Activo?", default=False)

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
        return self.id


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
    # rama = models.ForeignKey("Rama", on_delete=models.PROTECT)
    rama = models.CharField(max_length=1, choices=OPCIONES_RAMA)
    tipo_estudio = models.ForeignKey("TipoEstudio", on_delete=models.PROTECT)


class Evento(models.Model):
    nombre = models.CharField(primary_key=True, max_length=31)


class Licencia(models.Model):
    """Licencia de publicación de la memoria"""
    identificador = models.CharField(
        max_length=255,
        null=True,
        unique=True,
        help_text=_("Ver los identificadores estándar en https://spdx.org/licenses/"),
    )
    nombre = models.CharField(max_length=255)
    url = models.URLField("URL", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Linea(models.Model):
    nombre = models.CharField(max_length=31)
    programa = models.ForeignKey("Programa", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.programa} {self.nombre}"


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
    esta_activo = models.BooleanField("¿Activo?", default=True)
    centro = models.ForeignKey("Centro", on_delete=models.PROTECT)
    estudio = models.ForeignKey("Estudio", on_delete=models.PROTECT)


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
    convocatoria = models.ForeignKey("Convocatoria", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre_corto} {self.convocatoria}"


class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=31, null=True)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(_("Descripción"), blank=True, null=True)
    # publicar_memoria = models.BooleanField("¿Publicar la memoria?", default=True)
    financiacion = models.TextField(_("Financiación solicitada"), blank=True, null=True)
    ayuda = models.PositiveIntegerField(_("Ayuda solicitada"), blank=True, null=True)
    centro = models.ForeignKey("Centro", on_delete=models.PROTECT, null=True)
    convocatoria = models.ForeignKey("Convocatoria", on_delete=models.PROTECT)
    departamento = models.ForeignKey(
        "Departamento", on_delete=models.PROTECT, null=True
    )
    estudio = models.ForeignKey("Estudio", on_delete=models.PROTECT, null=True)
    licencia = models.ForeignKey("Licencia", on_delete=models.PROTECT, null=True)
    linea = models.ForeignKey("Linea", on_delete=models.PROTECT, null=True)
    programa = models.ForeignKey("Programa", on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse("proyecto_detail", args=[str(self.id)])

    def __str__(self):
        return self.codigo


class ParticipanteProyecto(models.Model):
    proyecto = models.ForeignKey("Proyecto", on_delete=models.PROTECT)
    tipo_participacion = models.ForeignKey(
        "TipoParticipacion", on_delete=models.PROTECT
    )
    usuario = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)


""" class Rama(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    nombre = models.CharField(max_length=63)
"""


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
