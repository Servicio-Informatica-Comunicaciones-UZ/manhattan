from django.db import models

# Create your models here.


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
    email = models.CharField(
        "correo electrónico", max_length=254, blank=True, null=True
    )
    url = models.CharField("URL", max_length=255, blank=True, null=True)
    nip_decano = models.PositiveIntegerField(blank=True, null=True)
    nombre_decano = models.CharField(max_length=255, blank=True, null=True)
    email_decano = models.CharField(max_length=254, blank=True, null=True)
    tratamiento_decano = models.CharField(max_length=25, blank=True, null=True)
    nip_secretario = models.PositiveIntegerField(blank=True, null=True)
    nombre_secretario = models.CharField(max_length=255, blank=True, null=True)
    email_secretario = models.CharField(max_length=254, blank=True, null=True)
    esta_activo = models.BooleanField("¿Activo?", default=False)

    def __str__(self):
        return f"{self.academico_id_nk} {self.rrhh_id_nk} {self.nombre}"

    class Meta:
        indexes = [
            models.Index(fields=["academico_id_nk"]),
            models.Index(fields=["rrhh_id_nk"]),
        ]


class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)
    academico_id_nk = models.IntegerField(
        "cód. académico", blank=True, db_index=True, null=True
    )
    rrhh_id_nk = models.CharField(
        "cód. RRHH", max_length=4, blank=True, null=True, unique=True
    )
    nombre = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(
        "correo electrónico", max_length=254, blank=True, null=True
    )
    email_secretaria = models.CharField(max_length=254, blank=True, null=True)
    nip_director = models.PositiveIntegerField(blank=True, null=True)
    nombre_director = models.CharField(max_length=255, blank=True, null=True)
    email_director = models.CharField(max_length=254, blank=True, null=True)

    def __str__(self):
        return f"{self.academico_id_nk} {self.rrhh_id_nk} {self.nombre}"
