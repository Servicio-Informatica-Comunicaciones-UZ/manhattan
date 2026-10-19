import json
import logging

import zeep
from annoying.functions import get_config
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from lxml.etree import XMLSyntaxError
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError as RequestConnectionError
from social_core.exceptions import AuthForbidden
from social_core.strategy import BaseStrategy

logger = logging.getLogger(__name__)


def get_identidad(strategy: BaseStrategy, backend, response, user, *args, **kwargs) -> None:
    """Actualiza el usuario con los datos obtenidos de Gestión de Identidades."""

    logger.info('[get_identidad] Iniciando para NIP=%s', user.username)

    try:
        _get_identidad(strategy, backend, response, user, *args, **kwargs)
    except Exception as exc:
        logger.exception(
            '[get_identidad] EXCEPCIÓN para NIP=%s: %s', user.username, exc
        )
        raise


def _get_identidad(strategy: BaseStrategy, backend, response, user, *args, **kwargs) -> None:
    """Lógica interna de actualización del usuario."""

    wsdl = get_config('WSDL_IDENTIDAD')
    session = Session()
    session.auth = HTTPBasicAuth(get_config('USER_IDENTIDAD'), get_config('PASS_IDENTIDAD'))

    try:
        client = zeep.Client(wsdl=wsdl, transport=zeep.transports.Transport(session=session))
    except RequestConnectionError:
        raise RequestConnectionError('No fue posible conectarse al WS de Identidades.')
    except XMLSyntaxError:
        raise XMLSyntaxError('El WS de Identidades no devolvió un XML válido.')
    except Exception as e:
        print(e)
        raise e

    response = client.service.obtenIdentidad(user.username)
    logger.info(
        '[get_identidad] NIP=%s | activo=%s | perfiles=%s | vinculaciones=%s | email=%s',
        user.username,
        getattr(response.identidad, 'activo', '?'),
        getattr(response.identidad, 'perfiles', '?'),
        getattr(response.identidad, 'vinculaciones', '?'),
        getattr(response.identidad, 'correoPrincipal', '?'),
    )

    if response.aviso:
        # El WS produjo una advertencia. La mostramos y seguimos.
        messages.warning(strategy.request, response.descripcionAviso)

    if response.error:
        # La comunicación con el WS fue correcta, pero éste devolvió un error. Finalizamos.
        raise Exception('WS Identidad: ' + response.descripcionResultado)

    identidad = response.identidad

    if identidad.activo == 'N':
        # El usuario existe en Identidades pero está marcado como inactivo.
        # Interrumpimos el pipeline limpiamente para evitar un bucle SAML.
        logger.warning(
            '[get_identidad] NIP=%s marcado como activo=N en Identidades. Login denegado.',
            user.username,
        )
        raise AuthForbidden(backend)

    user.first_name = identidad.nombre
    user.last_name = identidad.primerApellido
    user.last_name_2 = identidad.segundoApellido
    correo_personal = (
        identidad.correoPersonal if is_email_valid(identidad.correoPersonal) else None
    )
    correo_principal = (
        identidad.correoPrincipal if is_email_valid(identidad.correoPrincipal) else None
    )
    # El email es un campo NOT NULL en el modelo.
    user.email = correo_principal or correo_personal or ''
    user.is_active = identidad.activo != 'N'
    user.nombre_oficial = identidad.nombreAdmin
    user.numero_documento = identidad.documento
    user.sexo = identidad.sexo
    user.sexo_oficial = identidad.sexoAdmin
    user.tipo_documento = identidad.tipoDocumento
    user.centro_id_nks = json.dumps(identidad.centros)
    user.departamento_id_nks = json.dumps(identidad.departamentos)
    colectivos = identidad.perfiles
    cods_vinculaciones = identidad.vinculaciones
    if any(cod_adscritos in cods_vinculaciones for cod_adscritos in (12, 13, 42)):
        colectivos.append('ADS')
    if any(cod_adscritos in cods_vinculaciones for cod_adscritos in (25, 61)):
        colectivos.append('INV')  # Investigadores sin contrato pero con docencia
    user.colectivos = json.dumps(list(set(colectivos)))
    user.cuerpo_pod = identidad.cuerpoPod
    user.orcid = identidad.orcid if identidad.orcid != '-' else None

    logger.info(
        '[get_identidad] NIP=%s guardado. colectivos=%s is_active=%s',
        user.username, user.colectivos, user.is_active,
    )

    # user.save()
    strategy.storage.user.changed(user)


def is_email_valid(email: str) -> bool:
    """Validate email address"""
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True
