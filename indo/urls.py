from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

# from . import views
from .views import (
    AyudaView,
    HomePageView,
    InvitacionView,
    ParticipanteDeleteView,
    ProyectoCreateView,
    ProyectoDetailView,
    ProyectoPresentarView,
    ProyectoUpdateFieldView,
    ProyectosUsuarioListView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("summernote/", include("django_summernote.urls")),
    path("ayuda/", AyudaView.as_view(), name="ayuda"),
    path(
        "participante-proyecto/invitar/<int:proyecto_id>",
        InvitacionView.as_view(),
        name="participante_invitar",
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
        "proyecto/<int:pk>/presentar",
        ProyectoPresentarView.as_view(),
        name="proyecto_presentar",
    ),
    path(
        "proyecto/", ProyectosUsuarioListView.as_view(), name="proyectos_usuario_list"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
