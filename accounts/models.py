import json
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def get_or_none(self, **kwargs):
        """Devuelve el usuario con las propiedades indicadas, o `None` si no se encuentra."""
        try:
            return self.get(**kwargs)
        except CustomUser.DoesNotExist:
            return None


class CustomUser(AbstractUser):
    # Campos sobrescritos
    first_name = models.CharField(
        _("first name"), max_length=50, blank=True  # era: max_length=30
    )
    # Campos adicionales
    numero_documento = models.CharField(
        _("número de documento"),
        max_length=16,
        blank=True,
        null=True,
        help_text=_("DNI, NIE o pasaporte."),
    )
    tipo_documento = models.CharField(
        _("tipo de documento"),
        max_length=3,
        blank=True,
        null=True,
        help_text=_("DNI, NIE o pasaporte."),
    )
    last_name_2 = models.CharField(
        _("segundo apellido"), max_length=150, blank=True, null=True
    )
    sexo = models.CharField(max_length=1, blank=True, null=True)
    sexo_oficial = models.CharField(max_length=1, blank=True, null=True)
    nombre_oficial = models.CharField(max_length=50, blank=True, null=True)
    centro_id_nks = models.CharField(
        _("Cód. centros"), max_length=127, blank=True, null=True
    )
    departamento_id_nks = models.CharField(
        _("Cód. departamentos"), max_length=127, blank=True, null=True
    )
    colectivos = models.CharField(max_length=127, blank=True, null=True)

    # Metodos sobrescritos
    def get_full_name(self):
        """Devuelve el nombre completo (nombre y los dos apellidos)."""
        full_name = "%s %s %s" % (self.first_name, self.last_name, self.last_name_2)
        return full_name.strip()

    # Métodos adicionales
    def __str__(self):
        return self.username

    def get_colectivo_principal(self):
        """Devuelve el colectivo del usuario según el orden de prelación PDI>ADS>PAS>EST"""
        colectivos_del_usuario = json.loads(self.colectivos)
        for col in ("PDI", "ADS", "PAS", "EST"):
            if col in colectivos_del_usuario:
                return col
        return None

    # Custom Manager
    objects = CustomUserManager()
