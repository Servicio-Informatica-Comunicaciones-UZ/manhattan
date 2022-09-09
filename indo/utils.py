# Third-party
from django_tables2 import SingleTableView

# Django
from django.http import HttpRequest

# Local Django
from .models import Evento, Proyecto, Registro


class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_table_data(self):
        self.filter = self.filter_class(self.request.GET, queryset=super().get_table_data())
        if self.formhelper_class:
            self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_filter_name] = self.filter
        return context


def get_client_ip(request):
    """
    Devuelve la (presunta) IP del cliente.

    Véase <https://en.wikipedia.org/wiki/X-Forwarded-For>
    """
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[-1].strip()

    return request.META.get('REMOTE_ADDR')


def registrar_evento(
    request: HttpRequest, nombre_evento: str, descripcion: str, proyecto: Proyecto
) -> None:
    evento = Evento.objects.get(nombre=nombre_evento)
    ip_address = get_client_ip(request)

    registro = Registro(
        descripcion=descripcion,
        evento=evento,
        proyecto=proyecto,
        usuario=request.user,
        ip_address=ip_address,
    )
    registro.save()
