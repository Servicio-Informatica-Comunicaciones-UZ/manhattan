from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from social_django.utils import load_strategy, load_backend

# Create your views here.


def metadataView(request):
    complete_url = reverse("social:complete", args=("saml",))
    saml_backend = load_backend(
        load_strategy(request), "saml", redirect_uri=complete_url
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type="text/xml")
