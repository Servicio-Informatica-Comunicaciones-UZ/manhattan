import django_filters
from .models import Proyecto


class ProyectoFilter(django_filters.FilterSet):
    """Filtro para buscar proyectos por su estado."""

    class Meta:
        model = Proyecto
        fields = {
            'estado': ['exact'],
        }
        order_by = ['programa__nombre_corto', 'linea__nombre', 'titulo']


class ProyectoCentroFilter(django_filters.FilterSet):
    """Filtro para buscar proyectos por su centro."""

    class Meta:
        model = Proyecto
        fields = {
            'centro_id': ['exact'],
        }
        order_by = ['programa__nombre_corto', 'linea__nombre', 'titulo']
