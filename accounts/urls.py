from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Para evitar que un usuario ya autenticado pueda volver a la página de inicio de sesión
    path(
        "login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path("metadata", views.metadataView, name="metadata"),
]
