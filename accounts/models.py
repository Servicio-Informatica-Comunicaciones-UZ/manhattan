from __future__ import annotations

import json

import zeep
from annoying.functions import get_config, get_object_or_None
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from lxml.etree import XMLSyntaxError
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError as RequestConnectionError
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

from indo.models import Centro, Departamento

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
    cuerpo_pod = models.CharField(_('Cuerpo POD'), max_length=15, blank=True, null=True)
    orcid = models.CharField(max_length=19, blank=True, null=True)

    class Meta:
        ordering = (
            'last_name',
            'last_name_2',
            'first_name',
        )

    @property
    def id_nk_centros(self):
        """Devuelve una lista con los ID de los centros del usuario."""
        return set(json.loads(self.centro_id_nks)) if self.centro_id_nks else []

    @property
    def centros(self):
        """Devuelve una lista con los centros del usuario."""
        return list(
            filter(
                lambda x: x is not None and x.esta_activo,
                [
                    get_object_or_None(Centro, academico_id_nk=id_nk)
                    for id_nk in self.id_nk_centros
                ],
            )
        )

    @property
    def nombres_centros(self):
        """Devuelve una cadena con los nombres de los centros del usuario."""
        return ', '.join([centro.nombre for centro in self.centros])

    @property
    def id_nk_departamentos(self):
        """Devuelve una lista con los ID de los departamentos del usuario."""
        return set(json.loads(self.departamento_id_nks)) if self.departamento_id_nks else []

    @property
    def departamentos(self):
        """Devuelve una lista con los departamentos del usuario."""
        return list(
            filter(
                lambda x: x is not None,
                [
                    get_object_or_None(Departamento, academico_id_nk=id_nk)
                    for id_nk in self.id_nk_departamentos
                ],
            )
        )

    @property
    def nombres_departamentos(self):
        """Devuelve una cadena con los nombres de los departamentos del usuario."""
        return ', '.join([departamento.nombre for departamento in self.departamentos])

    @property
    def full_name(self):
        """Devuelve el nombre completo (nombre y los dos apellidos)."""
        return ' '.join(
            part.strip() for part in (self.first_name, self.last_name, self.last_name_2) if part
        )

    @property
    def apellidos_nombre(self):
        """Devuelve el nombre completo en formato «Apellido_1 Apellido_2, Nombre»."""
        nombre = self.first_name.strip() if self.first_name else ''
        apellidos = ' '.join(part.strip() for part in (self.last_name, self.last_name_2) if part)

        return f'{apellidos}, {nombre}'

    # Metodos sobrescritos
    def __str__(self):
        return self.username

    def get_full_name(self):
        """Devuelve el nombre completo (nombre y los dos apellidos)."""
        return self.full_name

    # Métodos adicionales

    def actualizar(self, request):
        """Actualiza el usuario con los datos de Gestión de Identidades."""
        get_identidad(load_strategy(request), None, self)

    def get_colectivo_principal(self):
        """Devuelve el colectivo principal del usuario.

        Se determina usando el orden de prelación PDI > PAS > ADS > EST.
        PDI y PAS pueden solicitar financiación, pero el profesorado de los centros adscritos no.
        """
        colectivos_del_usuario = json.loads(self.colectivos) if self.colectivos else []
        for col in ('PDI', 'PAS', 'ADS', 'EST'):
            if col in colectivos_del_usuario:
                return col
        return None

    def get_num_equipos(self, anyo):
        """Devuelve el número de equipos de trabajo en los que participa el usuario."""
        num_como_participante = (
            self.vinculaciones.filter(
                tipo_participacion='participante', proyecto__convocatoria_id=anyo
            )
            .exclude(proyecto__estado='ANULADO')
            .count()
        )
        num_como_coordinador = self.vinculaciones.filter(
            tipo_participacion__in=['coordinador', 'coordinador_principal'],
            proyecto__convocatoria_id=anyo,
            proyecto__estado='SOLICITADO',
        ).count()
        num_equipos = num_como_participante + num_como_coordinador
        return num_equipos

    @classmethod
    def crear_usuario(cls, request, nip: str) -> CustomUser:
        """Crea un registro de usuario con el NIP indicado y los datos de Gestión Identidades."""

        usuario = cls.objects.create_user(username=nip)
        try:
            get_identidad(load_strategy(request), None, usuario)
        except Exception as ex:
            # Si Gestión de Identidades devuelve un error, borramos el usuario
            # y finalizamos mostrando el mensaje de error.
            usuario.delete()
            raise ValidationError(ex)

        # HACK - Indicamos que la autenticación es vía Single Sign On con SAML.
        usuario_social = UserSocialAuth(
            uid=f'sir:{usuario.username}', provider='saml', user=usuario
        )
        usuario_social.save()

        return usuario

    @classmethod
    def get_nips_vinculacion(cls, cod_vinculacion):
        """Devuelve los NIPs que tengan el código de vinculación indicado.

        También devuelve la descripción de la advertencia en caso de producirse."""
        wsdl = get_config('WSDL_VINCULACIONES')
        session = Session()
        session.auth = HTTPBasicAuth(
            get_config('USER_VINCULACIONES'), get_config('PASS_VINCULACIONES')
        )

        try:
            client = zeep.Client(wsdl=wsdl, transport=zeep.transports.Transport(session=session))
        except RequestConnectionError:
            raise RequestConnectionError('No fue posible conectarse al WS de Vinculaciones.')
        except XMLSyntaxError:
            raise XMLSyntaxError('El WS de Identidades no devolvió un XML válido.')
        except Exception as e:
            print(e)
            raise e

        response = client.service.mostrarVinculaciones(cod_vinculacion)

        # Si el WS produce una advertencia, la devolveremos con el resultado para mostrarla.
        advertencia = response.descripcionAviso if response.aviso else None

        if response.error:
            # La comunicación con el WS fue correcta, pero éste devolvió un error. Finalizamos.
            raise Exception(response.descripcionResultado)

        return advertencia, response.nipsInteger

    # Custom Manager
    objects = CustomUserManager()
