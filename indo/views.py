from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    View,
    FormView,
)
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import (
    Convocatoria,
    Evento,
    ParticipanteProyecto,
    Proyecto,
    Registro,
    TipoParticipacion,
)


class AyudaView(TemplateView):
    template_name = "ayuda.html"


class HomePageView(TemplateView):
    template_name = "home.html"


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    """Crea una nueva solicitud de proyecto"""

    model = Proyecto
    template_name = "proyecto/new.html"
    fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]

    def form_valid(self, form):
        # Do custom logic on form data that has already been validated here
        form.instance.convocatoria = Convocatoria(2019)
        proyecto = form.save()
        self._guardar_coordinador(proyecto)
        self._registrar_creacion(proyecto)
        return redirect("proyecto_detail", proyecto.id)

    def _guardar_coordinador(self, proyecto):
        # Los PIET debe solicitarlos uno de los coordinadores del estudio ("coordinador principal")
        # quien podrá nombrar a otro coordinador.
        if proyecto.programa.nombre_corto == "PIET":
            tipo_participacion = "coordinador_principal"
        else:
            tipo_participacion = "coordinador"

        participanteProyecto = ParticipanteProyecto(
            proyecto=proyecto,
            tipo_participacion=TipoParticipacion(nombre=tipo_participacion),
            usuario=self.request.user,
        )
        participanteProyecto.save()

    def _registrar_creacion(self, proyecto):
        evento = Evento.objects.get(nombre="creacion_solicitud")
        registro = Registro(
            descripcion="Creación inicial de la solicitud",
            evento=evento,
            proyecto=proyecto,
        )
        registro.save()


class ProyectoDetailView(DetailView):
    model = Proyecto
    template_name = "proyecto/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        coordinador_principal = self.object.get_participante_or_none(
            "coordinador_principal"
        )
        context["coordinador_principal"] = coordinador_principal

        coordinador = self.object.get_participante_or_none("coordinador")
        context["coordinador"] = coordinador

        return context
