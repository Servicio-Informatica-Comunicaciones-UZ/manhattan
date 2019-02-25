from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class AyudaView(TemplateView):
    template_name = "ayuda.html"


class HomePageView(TemplateView):
    template_name = "home.html"
