import json
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
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
from django_summernote.widgets import SummernoteWidget

from .forms import InvitacionForm, ProyectoForm
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


class InvitacionView(LoginRequiredMixin, CreateView):
    """Formulario para invitar a una persona a un proyecto determinado."""

    # TODO: Comprobar permisos, estado del proyecto, fecha.
    form_class = InvitacionForm
    model = ParticipanteProyecto
    template_name = "participante-proyecto/invitar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto_id = self.kwargs["proyecto_id"]
        context["proyecto"] = Proyecto.objects.get(id=proyecto_id)

        # context["form"] = self.get_form()
        # This sets the initial value for the field:
        # context["form"].fields["proyecto_id"].initial = self.kwargs["proyecto_id"]

        return context

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        # Update the kwargs for the form init method with ours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        # We also send a user object to the form
        kwargs.update({'current_user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('proyecto_detail', kwargs = {'pk': self.kwargs["proyecto_id"]})

    def save():
        invitado = super.save(commit=False)
        invitado.tipo_participacion = TipoParticipacion("invitado")
        invitado.save()


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    """Crea una nueva solicitud de proyecto"""

    # TODO: Comprobar usuario para Proyectos de titulación y POU.
    # TODO: Comprobar fecha

    model = Proyecto
    template_name = "proyecto/new.html"
    # fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]
    form_class = ProyectoForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed, to do custom logic on form data.
        # It should return an HttpResponse.
        proyecto = form.save()
        self._guardar_coordinador(proyecto)
        self._registrar_creacion(proyecto)
        return redirect("proyecto_detail", proyecto.id)

    def get_form(self, form_class=None):
        """Devuelve el formulario añadiendo automáticamente el campo Convocatoria, que es requerido."""
        form = super(ProyectoCreateView, self).get_form(form_class)
        form.instance.convocatoria = Convocatoria(date.today().year)
        return form

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
    """Muestra una solicitud de proyecto."""

    # TODO: Comprobar permisos
    #   - Coordinadores, participantes/invitados, evaluadores.  Gestores.
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

        participantes = (
            self.object.participantes.filter(tipo_participacion="participante")
            .order_by("usuario__first_name", "usuario__last_name")
            .all()
        )
        context["participantes"] = participantes

        invitados = (
            self.object.participantes.filter(tipo_participacion="invitado")
            .order_by("usuario__first_name", "usuario__last_name")
            .all()
        )
        context["invitados"] = invitados

        context["campos"] = json.loads(self.object.programa.campos)

        return context


class ProyectoUpdateFieldView(LoginRequiredMixin, UpdateView):
    # TODO: Comprobar permisos - coordinadores
    #       Modificar estado, sólo para gestores
    #       No permitir modificar convocatoria, etc
    # TODO: Comprobar estado/fecha
    model = Proyecto
    template_name = "proyecto/update.html"

    def get_form_class(self, **kwargs):
        campo = self.kwargs["campo"]
        if campo not in (
            "centro",
            "convocatoria",
            "departamento",
            "licencia",
            "linea",
            "programa",
            "ayuda",
            "estado",
        ):
            return modelform_factory(
                Proyecto, fields=(campo,), widgets={campo: SummernoteWidget()}
            )
        self.fields = (campo,)
        return super().get_form_class()


class ProyectosUsuarioListView(LoginRequiredMixin, ListView):
    """Lista los proyectos coordinados por el usuario actual."""

    context_object_name = "proyectos"
    template_name = "proyecto/list.html"

    def get_queryset(self):
        # TODO ¿Listar sólo los de la convocatoria actual?
        usuario = self.request.user
        return Proyecto.objects.filter(
            participantes__tipo_participacion__in=[
                "coordinador",
                "coordinador_principal",
            ]
        ).filter(participantes__usuario=usuario)
