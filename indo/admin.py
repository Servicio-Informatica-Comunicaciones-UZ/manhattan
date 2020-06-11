from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Criterio, Opcion

# Register your models here.
admin.site.register(Criterio)
admin.site.register(Opcion)

admin.site.site_header = _('Administración de Manhattan')
admin.site.site_title = _('Administración de Manhattan')
admin.site.index_title = _('Inicio')
