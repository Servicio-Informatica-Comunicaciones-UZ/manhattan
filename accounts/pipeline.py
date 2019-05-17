import json
from django.db import connections


class EMailDesconocido(Exception):
    """
    Excepción elevada cuando el usuario no tiene establecida
    ninguna dirección de correo electrónico en Gestión de Identidades.
    """

    pass


class UsuarioNoEncontrado(Exception):
    """Excepción elevada cuando no se encuentra al usuario en Gestión de Identidades"""

    pass


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Return a row from a cursor as a dict."""
    columns = (col[0] for col in cursor.description)
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    else:
        raise UsuarioNoEncontrado(
            "Usuario desconocido. No se ha encontrado en Gestión de Identidades."
        )


def get_identidad(strategy, response, user, *args, **kwargs):
    """Actualiza el modelo del usuario con los datos obtenidos de Gestión de Identidades."""
    with connections["identidades"].cursor() as cursor:
        cursor.execute(
            "SELECT * FROM GESTIDEN.GI_V_IDENTIDAD WHERE NIP = %s", [user.username]
        )
        identidad = dictfetchone(cursor)
        cursor.execute(
            "SELECT * FROM GESTIDEN.GI_V_IDENTIDAD_PERFIL WHERE NIP = %s",
            [user.username],
        )
        perfiles = dictfetchall(cursor)
        cursor.execute(
            "SELECT * FROM GESTIDEN.GI_V_IDENTIDAD_VINCULACION WHERE NIP = %s",
            [user.username],
        )
        vinculaciones = dictfetchall(cursor)

    user.first_name = identidad.get("NOMBRE")
    user.last_name = identidad.get("APELLIDO_1")
    user.last_name_2 = identidad.get("APELLIDO_2")
    user.email = identidad.get("CORREO_PERSONAL") or identidad.get("CORREO_PRINCIPAL")
    # El email es un campo requerido en el modelo.
    if not user.email:
        raise EMailDesconocido("Usuario sin dirección de correo establecida.")
    user.nombre_oficial = identidad.get("NOMBRE_ADMIN")
    user.numero_documento = identidad.get("DOC_ID")
    user.sexo = identidad.get("SEXO")
    user.sexo_oficial = identidad.get("SEXO_ADMIN")
    user.tipo_documento = identidad.get("TIPO_DOC_ID")

    perfil_centro_id_nks = {
        perfil.get("COD_CENTRO")
        for perfil in perfiles
        if perfil.get("COD_CENTRO") not in (0, None)
    }
    vinculacion_centro_id_nks = {
        vinculacion.get("COD_CENTRO")
        for vinculacion in vinculaciones
        if vinculacion.get("COD_CENTRO") not in (0, None)
    }
    # Los objetos de tipo `set` no son serializables a JSON.
    centro_id_nks = list(perfil_centro_id_nks.union(vinculacion_centro_id_nks))
    user.centro_id_nks = json.dumps(centro_id_nks)

    perfil_departamento_id_nks = {
        perfil.get("COD_DEPARTAMENTO")
        for perfil in perfiles
        if perfil.get("COD_DEPARTAMENTO") not in (0, None)
    }
    vinculacion_departamento_id_nks = {
        vinculacion.get("COD_DEPARTAMENTO")
        for vinculacion in vinculaciones
        if vinculacion.get("COD_DEPARTAMENTO") not in (0, None)
    }
    departamento_id_nks = list(
        perfil_departamento_id_nks.union(vinculacion_departamento_id_nks)
    )
    user.departamento_id_nks = json.dumps(departamento_id_nks)

    colectivos = list({perfil.get("COD_PERFIL") for perfil in perfiles})
    # Si el usuario es PDI o PAS de un centro adscrito, añadimos el colectivo "ADS".
    cod_vinculaciones = {
        vinculacion.get("COD_VINCULACION") for vinculacion in vinculaciones
    }
    if any(cod_adscritos in cod_vinculaciones for cod_adscritos in (12, 13, 42)):
        colectivos.append("ADS")
    user.colectivos = json.dumps(colectivos)

    # user.save()
    strategy.storage.user.changed(user)
