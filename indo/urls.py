from django.urls import path

# from . import views
from .views import AyudaView, HomePageView, ProyectoCreateView, ProyectoDetailView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("ayuda/", AyudaView.as_view(), name="ayuda"),
    path("proyecto/new/", ProyectoCreateView.as_view(), name="proyecto_new"),
    path("proyecto/<int:pk>/", ProyectoDetailView.as_view(), name="proyecto_detail"),
]
