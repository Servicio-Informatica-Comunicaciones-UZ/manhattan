# standard library
import json

# third-party
import zeep
from annoying.functions import get_config
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError as RequestConnectionError

# Django
from django.contrib import messages
from django.core.validators import ValidationError, validate_email


def get_identidad(strategy, response, user, *args, **kwargs):
    """Actualiza el usuario con los datos obtenidos de Gestión de Identidades."""

    wsdl = get_config('WSDL_IDENTIDAD')
    session = Session()
    session.auth = HTTPBasicAuth(get_config('USER_IDENTIDAD'), get_config('PASS_IDENTIDAD'))

    try:
        client = zeep.Client(wsdl=wsdl, transport=zeep.transports.Transport(session=session))
    except RequestConnectionError:
        raise RequestConnectionError('No fue posible conectarse al WS de Identidades.')
    except Exception as e:
        print(e)
        raise e

    response = client.service.obtenIdentidad(user.username)
    if response.aviso:
        # El WS produjo una advertencia. La mostramos y seguimos.
        messages.warning(strategy.request, response.descripcionAviso)

    if response.error:
        # La comunicación con el WS fue correcta, pero éste devolvió un error. Finalizamos.
        raise Exception(response.descripcionResultado)

    identidad = response.identidad
    user.first_name = identidad.nombre
    user.last_name = identidad.primerApellido
    user.last_name_2 = identidad.segundoApellido
    correo_personal = identidad.correoPersonal if is_email_valid(identidad.correoPersonal) else None
    correo_principal = identidad.correoPrincipal if is_email_valid(identidad.correoPrincipal) else None
    # El email es un campo NOT NULL en el modelo.
    user.email = correo_personal or correo_principal or ''
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
    user.colectivos = json.dumps(colectivos)

    # user.save()
    strategy.storage.user.changed(user)


def is_email_valid(email):
    """Validate email address"""
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True
