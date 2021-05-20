from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    AyudaView,
    CorreccionVerView,
    CorrectorAnyadirView,
    CorrectorCesarView,
    CorrectorTableView,
    EvaluacionVerView,
    EvaluacionView,
    HomePageView,
    InvitacionView,
    MemoriaCorreccionUpdateView,
    MemoriaDetailView,
    MemoriaPresentarView,
    MemoriaUpdateFieldView,
    MemoriasAsignadasTableView,
    ParticipanteAceptarView,
    ParticipanteDeclinarView,
    ParticipanteDeleteView,
    ParticipanteRenunciarView,
    ProyectoAceptarView,
    ProyectoAnularView,
    ProyectosCierreEconomicoTableView,
    ProyectoCreateView,
    ProyectoDetailView,
    ProyectoCorrectorTableView,
    ProyectoCorrectorUpdateView,
    ProyectoEvaluacionesCsvView,
    ProyectoEvaluacionesTableView,
    ProyectoEvaluadorTableView,
    ProyectoEvaluadorUpdateView,
    ProyectoFichaView,
    ProyectoMemoriasTableView,
    ProyectoResolucionUpdateView,
    ProyectoTableView,
    ProyectoPresentarView,
    ProyectoUpdateFieldView,
    ProyectoUPTableView,
    ProyectoVerCondicionesView,
    ProyectosAceptadosTableView,
    ProyectosEvaluadosTableView,
    ProyectosNotificarView,
    ProyectosUsuarioView,
)


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('summernote/', include('django_summernote.urls')),
    path('ayuda/', AyudaView.as_view(), name='ayuda'),
    path(
        'corrector/mis-memorias/<int:anyo>/',
        MemoriasAsignadasTableView.as_view(),
        name='memorias_asignadas_table',
    ),
    path('corrector/<int:pk>/corregir/', MemoriaCorreccionUpdateView.as_view(), name='corregir'),
    path(
        'evaluador/mis-proyectos/<int:anyo>/',
        ProyectosEvaluadosTableView.as_view(),
        name='proyectos_evaluados_table',
    ),
    path('evaluador/<int:pk>/evaluacion/', EvaluacionView.as_view(), name='evaluacion'),
    path('gestion/corrector/', CorrectorTableView.as_view(), name='correctores_table'),
    path('gestion/corrector/anyadir/', CorrectorAnyadirView.as_view(), name='corrector_anyadir'),
    path(
        'gestion/corrector/cesar/',
        CorrectorCesarView.as_view(),
        name='corrector_cesar',
    ),
    # Listados de proyectos
    path('gestion/proyectos/<int:anyo>/', ProyectoTableView.as_view(), name='proyectos_table'),
    path(
        'gestion/proyectos/<int:anyo>/cierre-economico/',
        ProyectosCierreEconomicoTableView.as_view(),
        name='cierre_economico_table',
    ),
    path(
        'gestion/proyectos/<int:anyo>/evaluaciones/',
        ProyectoEvaluacionesTableView.as_view(),
        name='evaluaciones_table',
    ),
    path(
        'gestion/proyectos/<int:anyo>/csv_evaluaciones/',
        ProyectoEvaluacionesCsvView.as_view(),
        name='csv_evaluaciones',
    ),
    path(
        'gestion/proyectos/<int:anyo>/notificar/',
        ProyectosNotificarView.as_view(),
        name='notificar_proyectos',
    ),
    path(
        'gestion/proyectos/<int:anyo>/correctores/',
        ProyectoCorrectorTableView.as_view(),
        name='proyecto_corrector_table',
    ),
    path(
        'gestion/proyectos/<int:anyo>/memorias/',
        ProyectoMemoriasTableView.as_view(),
        name='memorias_table',
    ),
    path(
        'gestion/proyectos/<int:anyo>/unidades-planificacion/',
        ProyectoUPTableView.as_view(),
        name='up_table',
    ),
    path(
        'gestion/proyectos/<int:anyo>/evaluadores/',
        ProyectoEvaluadorTableView.as_view(),
        name='evaluadores_table',
    ),
    # Gestión de un proyecto
    path(
        'gestion/proyecto/<int:pk>/editar_corrector/',
        ProyectoCorrectorUpdateView.as_view(),
        name='corrector_update',
    ),
    path(
        'gestion/proyecto/<int:pk>/editar_evaluador/',
        ProyectoEvaluadorUpdateView.as_view(),
        name='evaluador_update',
    ),
    path(
        'gestion/proyecto/<int:pk>/editar_resolucion/',
        ProyectoResolucionUpdateView.as_view(),
        name='resolucion_update',
    ),
    path(
        'gestion/proyecto/<int:pk>/correccion/', CorreccionVerView.as_view(), name='ver_correccion'
    ),
    path(
        'gestion/proyecto/<int:pk>/evaluacion/', EvaluacionVerView.as_view(), name='ver_evaluacion'
    ),
    # Memoria
    path('memoria/<int:pk>/', MemoriaDetailView.as_view(), name='memoria_detail'),
    path(
        'memoria/<int:proyecto_id>/edit/<int:sub_pk>/',
        MemoriaUpdateFieldView.as_view(),
        name='memoria_update_field',
    ),
    path('memoria/<int:pk>/presentar/', MemoriaPresentarView.as_view(), name='memoria_presentar'),
    # Participante en proyecto
    path(
        'participante-proyecto/aceptar_invitacion/<int:proyecto_id>/',
        ParticipanteAceptarView.as_view(),
        name='participante_aceptar',
    ),
    path(
        'participante-proyecto/declinar_invitacion/',
        ParticipanteDeclinarView.as_view(),
        name='participante_declinar',
    ),
    path(
        'participante-proyecto/invitar/<int:proyecto_id>/',
        InvitacionView.as_view(),
        name='participante_invitar',
    ),
    path(
        'participante-proyecto/renunciar/',
        ParticipanteRenunciarView.as_view(),
        name='participante_renunciar',
    ),
    path(
        'participante-proyecto/<int:pk>/delete/',
        ParticipanteDeleteView.as_view(),
        name='participante_delete',
    ),
    # Proyecto
    path('proyecto/new/', ProyectoCreateView.as_view(), name='proyecto_new'),
    path('proyecto/<int:pk>/', ProyectoDetailView.as_view(), name='proyecto_detail'),
    path('proyecto/<int:pk>/ficha', ProyectoFichaView.as_view(), name='proyecto_ficha'),
    path(
        'proyecto/<int:pk>/edit/<campo>/',
        ProyectoUpdateFieldView.as_view(),
        name='proyecto_update_field',
    ),
    path(
        'proyecto/<int:pk>/aceptar-condiciones/',
        ProyectoAceptarView.as_view(),
        name='proyecto_aceptar',
    ),
    path(
        'proyecto/<int:pk>/ver-condiciones/',
        ProyectoVerCondicionesView.as_view(),
        name='proyecto_ver_condiciones',
    ),
    path('proyecto/<int:pk>/anular/', ProyectoAnularView.as_view(), name='proyecto_anular'),
    path(
        'proyecto/<int:pk>/presentar/', ProyectoPresentarView.as_view(), name='proyecto_presentar'
    ),
    path(
        'proyectos/<int:anyo>/mis-proyectos/', ProyectosUsuarioView.as_view(), name='mis_proyectos'
    ),
    path(
        'proyectos/<int:anyo>/aceptados/',
        ProyectosAceptadosTableView.as_view(),
        name='proyectos_aceptados',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
