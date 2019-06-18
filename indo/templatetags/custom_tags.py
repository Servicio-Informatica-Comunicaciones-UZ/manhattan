import urllib.parse

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe


register = template.Library()

# DEFAULT_TAGS defined in django.contrib.messages.constants
MESSAGE_ICONS = {
    "debug": '<i class="fas fa-bug"></i>',
    "info": '<i class="fas fa-info-circle"></i>',
    "success": '<i class="fas fa-check-circle"></i>',
    "warning": '<i class="fas fa-exclamation-triangle"></i>',
    "error": '<i class="fas fa-bomb"></i>',
}

MESSAGE_STYLES = {
    "debug": "alert-info",
    "info": "alert-info",
    "success": "alert-success",
    "warning": "alert-warning",
    "error": "alert-danger",
}


@register.simple_tag
def alert_icon(tag):
    return mark_safe(MESSAGE_ICONS[tag])


@register.simple_tag
def alert_style(tag):
    return MESSAGE_STYLES[tag]


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
