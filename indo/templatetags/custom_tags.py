# See <https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/>

import urllib.parse

import nh3

# import bleach
# from bleach.css_sanitizer import CSSSanitizer
from annoying.functions import get_config
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

# DEFAULT_TAGS defined in django.contrib.messages.constants
MESSAGE_ICONS = {
    'debug': '<i class="fas fa-bug"></i>',
    'info': '<i class="fas fa-info-circle"></i>',
    'success': '<i class="fas fa-check-circle"></i>',
    'warning': '<i class="fas fa-exclamation-triangle"></i>',
    'error': '<i class="fas fa-bomb"></i>',
}

MESSAGE_STYLES = {
    'debug': 'alert-info',
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger',
}


@register.simple_tag
def alert_icon(tag):
    return mark_safe(MESSAGE_ICONS[tag])


@register.simple_tag
def alert_style(tag):
    return MESSAGE_STYLES[tag]


@register.simple_tag
def sso_url():
    """Devuelve la URL del Single Sign On.

    Se debe indicar el IdP a usar, definido en `settings.py`.
    """
    return '{base}?{params}'.format(
        base=reverse('social:begin', kwargs={'backend': 'saml'}),
        params=urllib.parse.urlencode({'next': '/', 'idp': 'sir'}),
    )


@register.filter
def get_item(dictionary, key):
    """Devuelve el valor de la clave `key` en el diccionario `dictionary`."""
    return dictionary.get(key)


@register.filter
def get_obj_attr(obj, attr):
    """Devuelve el valor del atributo `attr` del objeto `obj`."""
    return getattr(obj, attr)


@register.filter
def get_attr_verbose_name(obj, attr):
    """Devuelve el nombre prolijo del atributo indicado."""
    return obj._meta.get_field(attr).verbose_name


@register.filter(name='has_group')
def has_group(user, group_name):
    """Comprueba si el usuario pertenece al grupo indicado."""
    return user.groups.filter(name=group_name).exists()


# See <https://bleach.readthedocs.io/en/latest/clean.html>
"""
cleaner = bleach.Cleaner(
    tags=bleach.sanitizer.ALLOWED_TAGS.union(get_config('ADDITIONAL_ALLOWED_TAGS')),
    attributes=get_config('ALLOWED_ATTRIBUTES'),
    css_sanitizer=CSSSanitizer(allowed_css_properties=get_config('ALLOWED_CSS_PROPERTIES')),
    protocols=get_config('ALLOWED_PROTOCOLS'),
    strip=True,
    strip_comments=True,
)


@register.filter
def limpiar(text):
    if text is None:
        return ''
    return mark_safe(cleaner.clean(text))
"""


@register.filter
def limpiar(text):
    if text is None:
        return ''
    return mark_safe(
        nh3.clean(
            text,
            tags=nh3.ALLOWED_TAGS,
            attributes=nh3.ALLOWED_ATTRIBUTES,
            strip_comments=True,
            url_schemes=get_config('ALLOWED_URL_SCHEMES'),
        )
    )


@register.filter
def concat(arg1, arg2):
    """Concatenate arg1 and arg2"""
    return str(arg1) + str(arg2)
