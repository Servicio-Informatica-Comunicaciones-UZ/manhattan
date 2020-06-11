import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Proyecto


class EvaluadoresTable(tables.Table):
    """Muestra los proyectos solicitados y el evaluador asignado a ellos."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    editar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_editar(self, record):
        enlace = reverse('evaluador_update', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title={_("Editar el evaluador")}
                aria-label={_("Editar el evaluador")}>
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'evaluador.full_name', 'editar')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class ProyectosEvaluadosTable(tables.Table):
    """Muestra los proyectos asignados a un usuario evaluador."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f"<a href='{enlace}'>{record.titulo}</a>")

    boton_evaluar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_boton_evaluar(self, record):
        enlace = reverse('evaluacion', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title={_("Evaluar el proyecto")}
          aria-label={_('Evaluar el proyecto')} class="btn btn-info btn-sm">
            <span class="fas fa-balance-scale" aria-hidden="true" style="display: inline;"></span>
            &nbsp;{_('Evaluar')}
          </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'boton_evaluar')
        empty_text = _('Por el momento no se le ha asignado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class ProyectosTable(tables.Table):
    """Muestra las solicitudes de proyecto presentadas."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f"<a href='{enlace}'>{record.titulo}</a>")

    coordinadores = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Coordinador(es)')
    )

    def render_coordinadores(self, record):
        coordinadores = record.get_coordinadores()
        enlaces = [f"<a href='mailto:{c.email}'>{c.get_full_name()}</a>" for c in coordinadores]
        return mark_safe(', '.join(enlaces))

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'coordinadores', 'estado')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20
