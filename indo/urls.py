from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    AyudaView,
    EvaluacionVerView,
    EvaluacionView,
    HomePageView,
    InvitacionView,
    MemoriaDetailView,
    MemoriaPresentarView,
    ParticipanteAceptarView,
    ParticipanteDeclinarView,
    ParticipanteDeleteView,
    ParticipanteRenunciarView,
    ProyectoAceptarView,
    ProyectoAnularView,
    ProyectoCreateView,
    ProyectoDetailView,
    ProyectoEvaluacionesCsvView,
    ProyectoEvaluacionesTableView,
    ProyectoEvaluadorTableView,
    ProyectoEvaluadorUpdateView,
    ProyectoResolucionUpdateView,
    ProyectoTableView,
    ProyectoPresentarView,
    ProyectoUpdateFieldView,
    ProyectosEvaluadosTableView,
    ProyectosNotificarView,
    ProyectosUsuarioView,
)


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('summernote/', include('django_summernote.urls')),
    path('ayuda/', AyudaView.as_view(), name='ayuda'),
    path(
        'evaluador/mis-proyectos/<int:anyo>/',
        ProyectosEvaluadosTableView.as_view(),
        name='proyectos_evaluados_table',
    ),
    path('evaluador/<int:pk>/evaluacion/', EvaluacionView.as_view(), name='evaluacion'),
    path('gestion/proyectos/<int:anyo>/', ProyectoTableView.as_view(), name='proyectos_table'),
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
        'gestion/proyectos/<int:anyo>/evaluadores/',
        ProyectoEvaluadorTableView.as_view(),
        name='evaluadores_table',
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
        'gestion/proyecto/<int:pk>/evaluacion/', EvaluacionVerView.as_view(), name='ver_evaluacion'
    ),
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
    path('memoria/<int:pk>/', MemoriaDetailView.as_view(), name='memoria_detail'),
    path('memoria/<int:pk>/presentar/', MemoriaPresentarView.as_view(), name='memoria_presentar'),
    path('proyecto/new/', ProyectoCreateView.as_view(), name='proyecto_new'),
    path('proyecto/<int:pk>/', ProyectoDetailView.as_view(), name='proyecto_detail'),
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
    path('proyecto/<int:pk>/anular/', ProyectoAnularView.as_view(), name='proyecto_anular'),
    path(
        'proyecto/<int:pk>/presentar/', ProyectoPresentarView.as_view(), name='proyecto_presentar'
    ),
    path(
        'proyecto/mis-proyectos/<int:anyo>/', ProyectosUsuarioView.as_view(), name='mis_proyectos'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
