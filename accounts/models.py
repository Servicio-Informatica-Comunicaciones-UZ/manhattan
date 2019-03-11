from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    # add additional fields in here
    first_name = models.CharField(
        _("first name"), max_length=50, blank=True
    )  # era: max_length=30
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
    centro = models.ForeignKey("indo.Centro", models.DO_NOTHING, blank=True, null=True)
    departamento = models.ForeignKey(
        "indo.Departamento", models.DO_NOTHING, blank=True, null=True
    )

    def __str__(self):
        return self.username
