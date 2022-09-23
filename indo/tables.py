# Third-party
import django_tables2 as tables

# Django
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Local Django
from .models import ParticipanteProyecto, Proyecto


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
        fields = ('username', 'full_name')
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

    def render_evaluadores(self, record):
        return ', '.join([evaluador.full_name for evaluador in record.evaluadores.all()])

    def render_editar(self, record):
        enlace = reverse('evaluadores_update', args=[record.id])
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Editar los evaluadores')}"
                aria-label="{_('Editar los evaluadores')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
        )

    # Ver <https://django-tables2.readthedocs.io/en/latest/pages/ordering.html>
    def order_numero_participantes(self, queryset, is_descending):
        # XXX Incompatible con la opción ONLY_FULL_GROUP_BY de MariaDB/MySQL
        queryset = queryset.annotate(
            num_participantes=Count(
                'participantes', filter=Q(participantes__tipo_participacion='participante')
            )
        ).order_by(('-' if is_descending else '') + 'num_participantes')
        return (queryset, True)

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
            'evaluadores',
            'editar',
        )
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class EvaluacionProyectosTable(tables.Table):
    """Muestra los proyectos presentados, enlaces a evaluaciones, y resolución de la Comisión."""

    def render_titulo(self, record):
        enlace = reverse('proyecto_detail', args=[record.id])
        return mark_safe(f'<a href="{enlace}">{record.titulo}</a>')

    # `empty_values` es necesario para que se muestre la renderización,
    # porque el campo no tiene ningún valor en la tabla.
    evaluaciones = tables.Column(empty_values=(), orderable=False, verbose_name='Evaluaciones')
    resolucion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Resolución'))

    def render_evaluaciones(self, record):
        enlaces = ''
        asignaciones = record.evaluadores_proyectos.all()
        for asignacion in asignaciones:
            if asignacion.ha_evaluado:
                enlaces += f'''<a href="{reverse('ver_evaluacion', args=[asignacion.id])}" title="{_('Ver evaluación')}"
                aria-label="{_('Ver evaluación')}"><span class="far fa-eye"></span></a> '''
        return mark_safe(enlaces) if enlaces else '—'

    def render_resolucion(self, record):
        enlace_ver = reverse('ver_resolucion', args=[record.id])
        enlace_editar = reverse('resolucion_update', args=[record.id])
        aceptacion = (
            f'''<span class="fas fa-eye text-success" title="{_('Aceptado')}"></span>'''
            if record.aceptacion_comision is True
            else f'''<span class="fas fa-eye text-danger" title="{_('Denegado')}">
                 </span>'''
            if record.aceptacion_comision is False
            else ''
        )
        return mark_safe(
            f'''<a href="{enlace_ver}" title="{_('Ver la resolución de la Comisión Evaluadora')}"
                aria-label="{_('Ver la resolución')}">{aceptacion}</a>

                <a href="{enlace_editar}" title="{_('Editar la resolución de la Comisión')}"
                aria-label="{_('Editar la resolución')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
            if record.valoraciones.first()
            else '—'
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = ('programa', 'linea', 'id', 'titulo', 'evaluaciones', 'resolucion')
        empty_text = _('Por el momento no se ha presentado ninguna solicitud de proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        per_page = 20


class MemoriasAsignadasTable(tables.Table):
    """Muestra las memorias asignadas a un usuario corrector."""

    memoria = tables.Column(empty_values=(), orderable=False, verbose_name=_('Memoria'))
    aceptacion_corrector = tables.BooleanColumn(null=True, verbose_name=_('Adm'))
    es_publicable = tables.BooleanColumn(null=True, verbose_name=_('Pub'))
    valoracion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Valoración'))
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
        if record.estado != 'MEM_PRESENTADA':
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
            'es_publicable',
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
        if record.estado in ('ACEPTADO', 'MEM_RECHAZADA'):
            return mark_safe(
                f'''<a href="{enlace}" title="{_('Ver la memoria del proyecto')}"
                    aria-label="{_('Ver la memoria del proyecto')}">
                    <span class="far fa-eye"></span>
                    </a>'''
            )
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Ver la memoria del proyecto')}"
                aria-label="{_('Ver la memoria del proyecto')}">
                <span class="far fa-eye text-success"></span>
                </a>'''
        )

    memoria = tables.Column(empty_values=(), orderable=False, verbose_name=_('Memoria'))
    aceptacion_corrector = tables.BooleanColumn(null=True, verbose_name=_('Adm'))
    es_publicable = tables.BooleanColumn(null=True, verbose_name=_('Pub'))
    valoracion = tables.Column(empty_values=(), orderable=False, verbose_name=_('Valoración'))

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

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            'programa',
            'linea',
            'id',
            'titulo',
            'memoria',
            'aceptacion_corrector',
            'es_publicable',
            'valoracion',
        )
        empty_text = _('Por el momento no se ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
        # per_page = 20


class ProyectosAceptadosTable(tables.Table):
    """Muestra los proyectos aceptados en una convocatoria (opcionalmente por centro)."""

    proyecto__linea = tables.Column(visible=False)
    proyecto__titulo = tables.Column(visible=False)
    proyecto__centro = tables.Column(visible=False)

    vinculo = tables.Column(
        empty_values=(), order_by=('proyecto.titulo',), verbose_name=_('Título')
    )

    def render_vinculo(self, record):
        enlace = reverse('proyecto_ficha', args=[record.proyecto.id])
        return mark_safe(f'<a href="{enlace}">{record.proyecto.titulo}</a>')

    usuario__full_name = tables.Column(verbose_name=_('Coordinador'))

    proyecto__descripcion_txt = tables.Column(verbose_name=_('Descripción'), visible=False)

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = ParticipanteProyecto
        fields = (
            'proyecto__programa',
            'proyecto__linea',
            'proyecto__id',
            'proyecto__titulo',
            'vinculo',
            'usuario__full_name',
            'proyecto__centro',
            'proyecto__descripcion_txt',
        )
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
        # La memoria tiene que estar aceptada para poder cerrar el proyecto.
        if not record.aceptacion_corrector:
            return '—'

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

    editar_id_uxxi = tables.Column(empty_values=(), orderable=False, verbose_name='')

    def render_editar_id_uxxi(self, record):
        enlace = reverse('proyecto_update_field', kwargs={'pk': record.id, 'campo': 'id_uxxi'})
        return mark_safe(
            f'''<a href="{enlace}" title="{_('Editar el número de proyecto Universitas XXI')}"
                aria-label="{_('Editar el número de proyecto Universitas XXI')}">
                  <span class="fas fa-pencil-alt"></span>
                </a>'''
        )

    class Meta:
        attrs = {'class': 'table table-striped table-hover cabecera-azul'}
        model = Proyecto
        fields = (
            # 'programa',
            'id',
            'titulo',
            'coordinadores',
            'unidad_planificacion',
            'ayuda_definitiva',
            'tipo_gasto',
            'id_uxxi',
            'editar_id_uxxi',
        )
        empty_text = _('Por el momento ningún coordinador ha aceptado ningún proyecto.')
        template_name = 'django_tables2/bootstrap4.html'
