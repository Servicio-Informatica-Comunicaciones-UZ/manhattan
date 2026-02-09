from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Convocatoria, Criterio, MemoriaApartado, MemoriaSubapartado, Opcion, Resolucion

# Register your models here.
# Register your models here.
class ConvocatoriaForm(forms.ModelForm):
    class Meta:
        model = Convocatoria
        fields = '__all__'
        widgets = {
            'num_max_participantes': forms.NumberInput(attrs={'autocomplete': 'off'}),
        }


@admin.register(Convocatoria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    form = ConvocatoriaForm


@admin.register(Criterio)
class Criterio(admin.ModelAdmin):
    fields = ('convocatoria', 'parte', 'peso', 'descripcion', 'tipo', 'programas')
    list_display = ('parte', 'peso', 'descripcion', 'programas')
    list_display_links = ('descripcion',)
    list_filter = ('convocatoria',)
    ordering = ('-convocatoria', 'parte', 'peso')


@admin.register(MemoriaApartado)
class MemoriaApartado(admin.ModelAdmin):
    list_display = ('numero', 'descripcion')
    list_display_links = ('descripcion',)
    list_filter = ('convocatoria',)
    ordering = ('-convocatoria', 'numero')


@admin.register(MemoriaSubapartado)
class MemoriaSubapartado(admin.ModelAdmin):
    list_display = ('numero_apartado', 'peso', 'descripcion')
    list_display_links = ('descripcion',)
    list_filter = ('apartado__convocatoria',)
    ordering = ('apartado__numero', 'peso')


@admin.register(Opcion)
class Opcion(admin.ModelAdmin):
    fields = ('criterio', 'puntuacion', 'descripcion')
    list_display = ('mini_criterio', 'puntuacion', 'descripcion')
    list_display_links = ('descripcion',)
    list_filter = ('criterio__convocatoria',)
    ordering = ('criterio__peso', 'puntuacion')

    @admin.display(description=_('Criterio'))
    def mini_criterio(self, obj):
        return obj.criterio.descripcion[:12]


@admin.register(Resolucion)
class Resolucion(admin.ModelAdmin):
    list_display = ('fecha', 'titulo')


admin.site.site_header = _('Administración de Manhattan')
admin.site.site_title = _('Administración de Manhattan')
admin.site.index_title = _('Inicio')
