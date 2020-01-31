from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    AyudaView,
    HomePageView,
    InvitacionView,
    ParticipanteAceptarView,
    ParticipanteDeclinarView,
    ParticipanteDeleteView,
    ParticipanteRenunciarView,
    ProyectoAnularView,
    ProyectoCreateView,
    ProyectoDetailView,
    ProyectoListView,
    ProyectoPresentarView,
    ProyectoUpdateFieldView,
    ProyectosUsuarioView,
)


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("summernote/", include("django_summernote.urls")),
    path("ayuda/", AyudaView.as_view(), name="ayuda"),
    path(
        "gestion/proyecto/list/<int:anyo>",
        ProyectoListView.as_view(),
        name="proyecto_list",
    ),
    path(
        "participante-proyecto/aceptar_invitacion/<int:proyecto_id>",
        ParticipanteAceptarView.as_view(),
        name="participante_aceptar",
    ),
    path(
        "participante-proyecto/declinar_invitacion",
        ParticipanteDeclinarView.as_view(),
        name="participante_declinar",
    ),
    path(
        "participante-proyecto/invitar/<int:proyecto_id>",
        InvitacionView.as_view(),
        name="participante_invitar",
    ),
    path(
        "participante-proyecto/renunciar",
        ParticipanteRenunciarView.as_view(),
        name="participante_renunciar",
    ),
    path(
        "participante-proyecto/<int:pk>/delete/",
        ParticipanteDeleteView.as_view(),
        name="participante_delete",
    ),
    path("proyecto/new/", ProyectoCreateView.as_view(), name="proyecto_new"),
    path("proyecto/<int:pk>/", ProyectoDetailView.as_view(), name="proyecto_detail"),
    path(
        "proyecto/<int:pk>/edit/<campo>",
        ProyectoUpdateFieldView.as_view(),
        name="proyecto_update_field",
    ),
    path(
        "proyecto/<int:pk>/anular/",
        ProyectoAnularView.as_view(),
        name="proyecto_anular",
    ),
    path(
        "proyecto/<int:pk>/presentar",
        ProyectoPresentarView.as_view(),
        name="proyecto_presentar",
    ),
    path(
        "proyecto/mis-proyectos/<int:anyo>",
        ProyectosUsuarioView.as_view(),
        name="mis_proyectos",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
