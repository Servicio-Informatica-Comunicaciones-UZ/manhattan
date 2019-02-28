import urllib.parse
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def lord_url():
    return "{base}?{params}".format(
        base=reverse("social:begin", kwargs={"backend": "saml"}),
        params=urllib.parse.urlencode({"next": "/", "idp": "lord"}),
    )
