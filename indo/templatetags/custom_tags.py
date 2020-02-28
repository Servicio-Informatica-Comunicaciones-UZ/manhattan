# See <https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/>

import bleach
import urllib.parse

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from annoying.functions import get_config

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
def lord_url():
    '''Devuelve la URL del Single Sign On.'''
    return '{base}?{params}'.format(
        base=reverse('social:begin', kwargs={'backend': 'saml'}),
        params=urllib.parse.urlencode({'next': '/', 'idp': 'lord'}),
    )


@register.filter
def get_obj_attr(obj, attr):
    '''Devuelve el valor del atributo `attr` del objeto `obj`.'''
    return getattr(obj, attr)


@register.filter
def get_attr_verbose_name(obj, attr):
    '''Devuelve el nombre prolijo del atributo indicado.'''
    return obj._meta.get_field(attr).verbose_name


@register.filter(name='has_group')
def has_group(user, group_name):
    '''Comprueba si el usuario pertenece al grupo indicado.'''
    return user.groups.filter(name=group_name).exists()


# See <https://bleach.readthedocs.io/en/latest/clean.html>
cleaner = bleach.Cleaner(
    tags=(bleach.sanitizer.ALLOWED_TAGS + get_config('ADDITIONAL_ALLOWED_TAGS')),
    attributes=get_config('ALLOWED_ATTRIBUTES'),
    styles=get_config('ALLOWED_STYLES'),
    protocols=get_config('ALLOWED_PROTOCOLS'),
    strip=True,
    strip_comments=True,
)


@register.filter
def limpiar(text):
    return mark_safe(cleaner.clean(text))
