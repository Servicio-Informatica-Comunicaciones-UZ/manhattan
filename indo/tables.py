import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Proyecto


class ProyectosTable(tables.Table):
    def render_titulo(self, record):
        enlace = reverse("proyecto_detail", args=[record.id])
        return mark_safe(f"<a href='{enlace}'>{record.titulo}</a>")

    coordinadores = tables.Column(
        empty_values=(), orderable=False, verbose_name=_("Coordinador(es)")
    )

    def render_coordinadores(self, record):
        coordinadores = record.get_coordinadores()
        enlaces = [
            f"<a href='mailto:{c.email}'>{c.get_full_name()}</a>" for c in coordinadores
        ]
        return mark_safe(", ".join(enlaces))

    class Meta:
        attrs = {"class": "table table-striped table-hover cabecera-azul"}
        model = Proyecto
        fields = ("programa", "linea", "titulo", "coordinadores", "estado")
        empty_text = _(
            "Por el momento no se ha presentado ninguna solicitud de proyecto."
        )
        template_name = "django_tables2/bootstrap4.html"
        per_page = 20
