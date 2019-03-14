from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from social_django.utils import load_strategy, load_backend


def metadataView(request):
    """Muestra los metadatos para el Proveedor de Identidad (IdP) de SAML"""
    complete_url = reverse("social:complete", args=("saml",))
    saml_backend = load_backend(
        load_strategy(request), "saml", redirect_uri=complete_url
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type="text/xml")


class UserdataView(LoginRequiredMixin, View):
    """Muestra los datos del usuario."""

    def get(self, request, *args, **kwargs):
        context = {}
        context["datos_usuario"] = {
            field.name: field.value_to_string(request.user)
            for field in request.user._meta.fields
        }
        return render(request, "registration/userdata.html", context=context)
