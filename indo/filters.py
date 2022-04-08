import django_filters
from .models import ParticipanteProyecto, Proyecto


class ProyectoFilter(django_filters.FilterSet):
    """Filtro para buscar proyectos por su estado."""

    class Meta:
        model = Proyecto
        fields = {'estado': ['exact']}
        order_by = ['programa__nombre_corto', 'linea__nombre', 'titulo']


class ParticipanteProyectoCentroFilter(django_filters.FilterSet):
    """Filtro para buscar proyectos por su centro."""

    class Meta:
        model = ParticipanteProyecto
        fields = {'proyecto__centro__academico_id_nk': ['exact']}
        order_by = [
            'proyecto__programa__nombre_corto',
            'proyecto__linea__nombre',
            'proyecto__titulo',
        ]
