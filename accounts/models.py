# Standard library
import json

# Third-party
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

# Django
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# local Django
from .pipeline import get_identidad


class CustomUserManager(UserManager):
    def get_or_none(self, **kwargs):
        """Devuelve el usuario con las propiedades indicadas.

        Si no se encuentra, devuelve `None`.
        """
        try:
            return self.get(**kwargs)
        except CustomUser.DoesNotExist:
            return None


class CustomUser(AbstractUser):
    AbstractUser._meta.get_field('username').verbose_name = _('NIP')  # Cambio verbose_name
    AbstractUser._meta.get_field('last_name').verbose_name = _(
        'primer apellido'
    )  # Cambio verbose_name
    # Campos sobrescritos
    first_name = models.CharField(_('first name'), max_length=50, blank=True)  # era: max_length=30
    # Campos adicionales
    numero_documento = models.CharField(
        _('número de documento'),
        max_length=16,
        blank=True,
        null=True,
        help_text=_('DNI, NIE o pasaporte.'),
    )
    tipo_documento = models.CharField(
        _('tipo de documento'),
        max_length=3,
        blank=True,
        null=True,
        help_text=_('DNI, NIE o pasaporte.'),
    )
    last_name_2 = models.CharField(_('segundo apellido'), max_length=150, blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True)
    sexo_oficial = models.CharField(max_length=1, blank=True, null=True)
    nombre_oficial = models.CharField(max_length=50, blank=True, null=True)
    centro_id_nks = models.CharField(_('Cód. centros'), max_length=127, blank=True, null=True)
    departamento_id_nks = models.CharField(
        _('Cód. departamentos'), max_length=127, blank=True, null=True
    )
    colectivos = models.CharField(max_length=127, blank=True, null=True)

    @property
    def full_name(self):
        """Devuelve el nombre completo (nombre y los dos apellidos)."""
        return ' '.join(
            part.strip() for part in (self.first_name, self.last_name, self.last_name_2) if part
        )

    # Metodos sobrescritos
    def get_full_name(self):
        """Devuelve el nombre completo (nombre y los dos apellidos)."""
        return self.full_name

    # Métodos adicionales
    def __str__(self):
        return self.username

    def get_colectivo_principal(self):
        """Devuelve el colectivo principal del usuario.

        Se determina usando el orden de prelación PDI > ADS > PAS > EST.
        """
        colectivos_del_usuario = json.loads(self.colectivos) if self.colectivos else []
        for col in ('PDI', 'ADS', 'PAS', 'EST'):
            if col in colectivos_del_usuario:
                return col
        return None

    def get_num_equipos(self, anyo):
        '''Devuelve el número de equipos de trabajo en los que participa el usuario.'''
        num_como_participante = self.vinculaciones.filter(
            tipo_participacion='participante', proyecto__convocatoria_id=anyo
        ).count()
        num_como_coordinador = self.vinculaciones.filter(
            tipo_participacion__in=['coordinador', 'coordinador_principal'],
            proyecto__convocatoria_id=anyo,
            proyecto__estado='SOLICITADO',
        ).count()
        num_equipos = num_como_participante + num_como_coordinador
        return num_equipos

    @classmethod
    def crear_usuario(cls, request, nip):
        """Crea un registro de usuario con el NIP indicado y los datos de Gestión de Identidades."""

        usuario = cls.objects.create_user(username=nip)
        try:
            get_identidad(load_strategy(request), None, usuario)
        except Exception as ex:
            # Si Gestión de Identidades devuelve un error, borramos el usuario
            # y finalizamos mostrando el mensaje de error.
            usuario.delete()
            raise ValidationError('ERROR: ' + str(ex))

        # HACK - Indicamos que la autenticación es vía Single Sign On con SAML.
        usuario_social = UserSocialAuth(
            uid=f'lord:{usuario.username}', provider='saml', user=usuario
        )
        usuario_social.save()

        return usuario

    # Custom Manager
    objects = CustomUserManager()
