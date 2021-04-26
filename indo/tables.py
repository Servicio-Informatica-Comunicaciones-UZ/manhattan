import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Proyecto


class CorrectoresTable(tables.Table):
    """Muestra los usuarios del grupo Correctores."""

    full_name = tables.Column(orderable=False, verbose_name=_('Nombre completo'))
    eliminar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_eliminar(self, record):
        return mark_safe(
            f'''<button
                    class="btn-no-button prepararCesar"
                    data-id="{record.id}"
                    data-nombre="{record.full_name}"
                    data-toggle="modal"
                    data-target="#cesarModal"
                >
                    <span
                        class="fas fa-trash-alt text-danger"
                        title="{_('Cesar al corrector')}"
                        aria-label="{_('Cesar al corrector')}"
                    ></span>
                </button>
            '''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = get_user_model()
        fields = (
            'username',
            'full_name',
        )
        empty_text = _('Por el momento no hay ningún corrector.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class ProyectoCorrectorTable(tables.Table):
    """Muestra los proyectos aceptados y el corrector de memorias asignado a ellos."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    editar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_editar(self, record):
        enlace = reverse('corrector_update', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Editar el corrector')}"
                aria-label="{_('Editar el corrector')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'corrector__full_name', 'editar')
        empty_text = _('Por el momento ningún coordinador ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class EvaluadoresTable(tables.Table):
    """Muestra los proyectos solicitados y el evaluador asignado a ellos."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    editar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_editar(self, record):
        enlace = reverse('evaluador_update', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Editar el evaluador')}"
                aria-label="{_('Editar el evaluador')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'evaluador__full_name', 'editar')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class EvaluacionProyectosTable(tables.Table):
    """Muestra los proyectos presentados y enlaces a su evaluación y resolución de la Comisión."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    evaluacion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Evaluación'))
    resolucion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Resolución'))

    def render_evaluacion(self, record):
        enlace = reverse('ver_evaluacion', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la evaluación')}"
                aria-label="{_('Ver la evaluación')}">
                  <span class="far fa-eye"></span>
                </a>'''
            if record.valoraciones.first()
            else '—'
        )

    def render_resolucion(self, record):
        enlace = reverse('resolucion_update', args=[record.id])
        aceptacion = (
            f'''<span class="fas fa-check-circle text-success" title="{_('Aceptado')}"></span>'''
            if record.aceptacion_comision is True
            else f'''<span class="fas fa-times-circle text-danger" title="{_('Denegado')}">
                 </span>'''
            if record.aceptacion_comision is False
            else ''
        )
        return mark_safe(
            f'''{aceptacion} <a href="{enlace}" title="{_('Editar la resolución de la Comisión')}"
                aria-label="{_('Editar la resolución')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
            if record.valoraciones.first()
            else '—'
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'evaluacion', 'resolucion')
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
            f'''<a href="{enlace}" title="{_('Evaluar el proyecto')}"
          aria-label="{_('Evaluar el proyecto')}" class="btn btn-info btn-sm">
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
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    coordinadores = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Coordinador(es)')
    )

    def render_coordinadores(self, record):
        coordinadores = record.get_coordinadores()
        enlaces = [f'<a href="mailto:{c.email}">{c.get_full_name()}</a>' for c in coordinadores]
        return mark_safe(', '.join(enlaces))

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'titulo', 'coordinadores', 'estado')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20
