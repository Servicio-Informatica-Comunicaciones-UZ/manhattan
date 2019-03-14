import json
from django.db import connections


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Return a row from a cursor as a dict."""
    columns = (col[0] for col in cursor.description)
    return dict(zip(columns, cursor.fetchone()))


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
    user.colectivos = colectivos

    # user.save()
    strategy.storage.user.changed(user)

