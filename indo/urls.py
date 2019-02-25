from django.urls import path

# from . import views
from .views import AyudaView, HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("ayuda/", AyudaView.as_view(), name="ayuda"),
]
