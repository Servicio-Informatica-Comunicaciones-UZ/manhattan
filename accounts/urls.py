# from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # `manhattan_project.urls` incluye `django_social.urls`,
    # que define `/login/saml` y `/login/complete`.
    # Evita que un usuario ya autenticado pueda volver a la página de inicio de sesión
    # path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('login/', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    # Logout personalizado para solicitar el fin de la sesión SAML.
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # Finalizar la sesión SAML.
    path('sls/', views.SlsView.as_view(), name='sls'),
    # Muestra los metadatos para el Proveedor de Identidad (IdP) de SAML.
    path('metadata', views.metadata_xml, name='metadata'),
    # Muestra los datos del usuario.
    path('userdata', views.UserdataView.as_view(), name='userdata'),
]
