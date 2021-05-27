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
        fields = ('programa', 'linea', 'id', 'titulo', 'corrector__full_name', 'editar')
        empty_text = _('Por el momento ningún coordinador ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class EvaluadoresTable(tables.Table):
    """Muestra los proyectos solicitados y el evaluador asignado a ellos."""

    visto_bueno_centro = tables.Column(empty_values=(), verbose_name='VBC')
    visto_bueno_estudio = tables.Column(empty_values=(), verbose_name='VBE')
    numero_participantes = tables.Column(empty_values=(), verbose_name='P')
    editar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    def render_visto_bueno_centro(self, record):
        if not record.programa.requiere_visto_bueno_centro:
            return '—'

        return mark_safe(
            f'''<span class="text-success" title="{_('Aceptado')}">✔</span>'''
            if record.visto_bueno_centro is True
            else f'''<span class="text-danger" title="{_('Rechazado')}">✘</span>'''
            if record.visto_bueno_centro is False
            else f'''<span class="text-secondary" title="{_('Pendiente')}">⁇</span>'''
        )

    def render_visto_bueno_estudio(self, record):
        if not record.programa.requiere_visto_bueno_estudio:
            return '—'

        return mark_safe(
            f'''<span class="text-success" title="{_('Aceptado')}">✔</span>'''
            if record.visto_bueno_estudio is True
            else f'''<span class="text-danger" title="{_('Rechazado')}">✘</span>'''
            if record.visto_bueno_estudio is False
            else f'''<span class="text-secondary" title="{_('Pendiente')}">⁇</span>'''
        )

    def render_numero_participantes(self, record):
        if record.numero_participantes == 0:
            return mark_safe(
                f'''<span style="font-weight: bold;" class="text-danger">
                  {record.numero_participantes}
                </span>'''
            )
        return record.numero_participantes

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
        fields = (
            'programa',
            'linea',
            'id',
            'titulo',
            'visto_bueno_centro',
            'visto_bueno_estudio',
            'numero_participantes',
            'evaluador__full_name',
            'editar',
        )
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
        fields = ('programa', 'linea', 'id', 'titulo', 'evaluacion', 'resolucion')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class MemoriasAsignadasTable(tables.Table):
    """Muestra las memorias asignadas a un usuario corrector."""

    memoria = tables.Column(empty_values=(), orderable=False, verbose_name=_('Memoria'))
    valoracion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Valoración'))
    aceptacion_corrector = tables.BooleanColumn(null=True, verbose_name='Admitida')
    boton_valorar = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f"<a href='{enlace}'>{record.titulo}</a>")

    def render_memoria(self, record):
        enlace = reverse('memoria_detail', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la memoria del proyecto')}"
                aria-label="{_('Ver la memoria del proyecto')}">
                  <span class="far fa-eye"></span>
                </a>'''
        )

    def render_valoracion(self, record):
        enlace = reverse('ver_correccion', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la valoración del corrector de la memoria')}"
                aria-label="{_('Ver la valoración del corrector de la memoria')}">
                  <span class="far fa-eye"></span>
                </a>'''
            if record.aceptacion_corrector is not None
            else '—'
        )

    def render_boton_valorar(self, record):
        if record.aceptacion_corrector is not None:
            return ''

        enlace = reverse('corregir', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Valorar la memoria')}"
          aria-label="{_('Valorar la memoria')}" class="btn btn-info btn-sm">
            <span class="fas fa-balance-scale" aria-hidden="true" style="display: inline;"></span>
            &nbsp;{_('Valorar')}
          </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            'programa',
            'linea',
            'titulo',
            'memoria',
            'aceptacion_corrector',
            'valoracion',
            'boton_valorar',
        )
        empty_text = _('Por el momento no se le ha asignado ninguna memoria.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class MemoriaProyectosTable(tables.Table):
    """Muestra los proyectos aceptados y enlaces a su memoria y dictamen del corrector."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    def render_memoria(self, record):
        enlace = reverse('memoria_detail', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la memoria del proyecto')}"
                aria-label="{_('Ver la memoria del proyecto')}">
                  <span class="far fa-eye"></span>
                </a>'''
        )

    memoria = tables.Column(empty_values=(), orderable=False, verbose_name=_('Memoria'))
    valoracion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Valoración'))
    aceptacion_corrector = tables.BooleanColumn(null=True, verbose_name=_('Adm'))
    es_publicable = tables.BooleanColumn(null=True, verbose_name=_('Pub'))

    def render_valoracion(self, record):
        enlace = reverse('ver_correccion', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la valoración del corrector de la memoria')}"
                aria-label="{_('Ver la valoración del corrector de la memoria')}">
                  <span class="far fa-eye"></span>
                </a>'''
            if record.aceptacion_corrector is not None
            else '—'
        )

    def render_aceptacion_corrector(self, record):
        return mark_safe(
            f'''<span class="fas fa-check-circle text-success" title="{_('Admitida')}"></span>'''
            if record.aceptacion_corrector is True
            else f'''<span class="fas fa-times-circle text-danger" title="{_('No admitida')}">
                 </span>'''
            if record.aceptacion_corrector is False
            else '—'
        )

    def render_es_publicable(self, record):
        return mark_safe(
            f'''<span class="fas fa-check-circle text-success" title="{_('Publicable')}"></span>'''
            if record.es_publicable is True
            else f'''<span class="fas fa-times-circle text-danger" title="{_('No publicable')}">
                 </span>'''
            if record.es_publicable is False
            else '—'
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            'programa',
            'linea',
            'id',
            'titulo',
            'memoria',
            'valoracion',
            'aceptacion_corrector',
            'es_publicable',
        )
        empty_text = _('Por el momento no se ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        # per_page = 20


class ProyectosAceptadosTable(tables.Table):
    """Muestra los proyectos aceptados, y el centro de su coordinador."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_ficha', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    coordinador = tables.Column(orderable=False, verbose_name=_('Coordinador'))

    def render_coordinador(self, record):
        return record.coordinador.full_name

    centro_coordinador = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Centro del coordinador')
    )

    def render_centro_coordinador(self, record):
        return record.coordinador.nombres_centros

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'id', 'titulo', 'coordinador', 'centro_coordinador')
        empty_text = _('Por el momento ningún coordinador ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'


class ProyectosCierreEconomicoTable(tables.Table):
    """Muestra los proyectos aceptados y su cierre económico."""

    aceptacion_corrector = tables.BooleanColumn(null=True, verbose_name=_('Mem adm'))
    aceptacion_economico = tables.BooleanColumn(null=True, verbose_name=_('Cierre económico'))

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    def render_aceptacion_corrector(self, record):
        return mark_safe(
            f'''<span class="fas fa-check-circle text-success" title="{_('Admitida')}"></span>'''
            if record.aceptacion_corrector is True
            else f'''<span class="fas fa-times-circle text-danger" title="{_('No admitida')}">
                 </span>'''
            if record.aceptacion_corrector is False
            else '—'
        )

    def render_aceptacion_economico(self, record):
        if record.aceptacion_economico:
            return mark_safe(
                f'''<span class="fas fa-check-circle text-success" title="{_('Cerrado')}">
                </span>'''
            )

        enlace = reverse(
            'proyecto_update_field', kwargs={'pk': record.id, 'campo': 'aceptacion_economico'}
        )
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Cerrar económicamente')}"
                aria-label="{_('Cerrar económicamente')}">
                <span class="fas fa-pencil-alt"></span>
            </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            'programa',
            'linea',
            'id',
            'titulo',
            'aceptacion_corrector',
            'aceptacion_economico',
        )
        empty_text = _('Por el momento no se ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        # per_page = 20


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
    """Muestra las solicitudes de proyecto introducidas."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    coordinadores = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Coordinador(es)')
    )

    def render_coordinadores(self, record):
        coordinadores = record.get_coordinadores()
        enlaces = [f'<a href="mailto:{c.email}">{c.full_name}</a>' for c in coordinadores]
        return mark_safe(', '.join(enlaces))

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'id', 'titulo', 'coordinadores', 'estado')
        empty_text = _('Por el momento no se ha introducido ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class ProyectoUPTable(tables.Table):
    """Muestra los proyectos aceptados, su Unidad de Planificación y gastos autorizados."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    coordinadores = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Coordinador(es)')
    )

    def render_coordinadores(self, record):
        coordinadores = record.get_coordinadores()
        enlaces = [f'<a href="mailto:{c.email}">{c.full_name}</a>' for c in coordinadores]
        return mark_safe(', '.join(enlaces))

    unidad_planificacion = tables.Column(
        empty_values=(), orderable=False, verbose_name=_('Unidad de planificación')
    )

    def render_unidad_planificacion(self, record):
        return record.get_unidad_planificacion() or '—'

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            'programa',
            'id',
            'titulo',
            'coordinadores',
            'unidad_planificacion',
            'ayuda_concedida',
            'tipo_gasto',
        )
        empty_text = _('Por el momento ningún coordinador ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
