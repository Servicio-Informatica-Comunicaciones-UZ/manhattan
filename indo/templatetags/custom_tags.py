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


@register.filter
def get_obj_attr(obj, attr):
    """Devuelve el valor del atributo `attr` del objeto `obj`"""
    return getattr(obj, attr)


@register.filter
def get_attr_verbose_name(obj, attr):
    """Devuelve el nombre prolijo del atributo indicado"""
    return obj._meta.get_field(attr).verbose_name
