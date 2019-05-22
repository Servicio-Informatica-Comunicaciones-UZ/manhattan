import json
from datetime import date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.models import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_summernote.widgets import SummernoteWidget

from templated_email import send_templated_mail

from .forms import InvitacionForm, ProyectoForm
from .models import (
    Convocatoria,
    Evento,
    ParticipanteProyecto,
    Proyecto,
    Registro,
    TipoParticipacion,
)


class ChecksMixin(UserPassesTestMixin):
    """Proporciona comprobaciones para autorizar o no una acción a un usuario."""

    def es_coordinador(self, proyecto_id):
        """Devuelve si el usuario actual es coordinador del proyecto indicado."""
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        coordinadores_participantes = proyecto.participantes.filter(
            tipo_participacion__in=["coordinador", "coordinador_principal"]
        ).all()
        usuarios_coordinadores = list(
            map(lambda p: p.usuario, coordinadores_participantes)
        )
        self.permission_denied_message = _("Usted no es coordinador de este proyecto.")

        return usuario_actual in usuarios_coordinadores

    def es_participante(self, proyecto_id):
        """Devuelve si el usuario actual es participante del proyecto indicado."""
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = proyecto.participantes.filter(
            usuario=usuario_actual, tipo_participacion="participante"
        ).all()
        self.permission_denied_message = _("Usted no es participante de este proyecto.")

        return True if pp else False

    def es_invitado(self, proyecto_id):
        """Devuelve si el usuario actual es invitado del proyecto indicado."""
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = proyecto.participantes.filter(
            usuario=usuario_actual, tipo_participacion="invitado"
        ).all()
        self.permission_denied_message = _("Usted no está invitado a este proyecto.")

        return True if pp else False

    def esta_vinculado(self, proyecto_id):
        """Devuelve si el usuario actual está vinculado al proyecto indicado."""
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = (
            proyecto.participantes.filter(usuario=usuario_actual)
            .exclude(tipo_participacion="invitacion_rehusada")
            .all()
        )
        self.permission_denied_message = _("Usted no está vinculado a este proyecto.")

        return True if pp else False

    def es_pas_o_pdi(self):
        """
        Devuelve si el usuario actual es PAS o PDI de la UZ o de sus centros adscritos.
        """
        usuario_actual = self.request.user
        colectivos_del_usuario = json.loads(usuario_actual.colectivos)
        self.permission_denied_message = _("Usted no es PAS ni PDI.")

        return any(
            col_autorizado in colectivos_del_usuario
            for col_autorizado in ["PAS", "ADS", "PDI"]
        )


class AyudaView(TemplateView):
    template_name = "ayuda.html"


class HomePageView(TemplateView):
    template_name = "home.html"


class InvitacionView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Muestra un formulario para invitar a una persona a un proyecto determinado."""

    form_class = InvitacionForm
    model = ParticipanteProyecto
    template_name = "participante-proyecto/invitar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto_id = self.kwargs["proyecto_id"]
        context["proyecto"] = Proyecto.objects.get(id=proyecto_id)
        return context

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        # Update the kwargs for the form init method with ours
        kwargs.update(self.kwargs)  # self.kwargs contains all URL conf params
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            "proyecto_detail", kwargs={"pk": self.kwargs["proyecto_id"]}
        )

    def test_func(self):
        # TODO: Comprobar estado del proyecto, fecha.
        return self.es_coordinador(self.kwargs["proyecto_id"])


class ParticipanteAceptarView(LoginRequiredMixin, RedirectView):
    """Aceptar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("proyectos_usuario_list")

    def post(self, request, *args, **kwargs):
        proyecto_id = kwargs.get("proyecto_id")
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = get_object_or_404(
            ParticipanteProyecto,
            proyecto_id=proyecto_id,
            usuario=usuario_actual,
            tipo_participacion="invitado",
        )
        pp.tipo_participacion_id = "participante"
        pp.save()

        messages.success(
            request,
            _(f"Ha pasado a ser participante del proyecto «{proyecto.titulo}»."),
        )
        return super().post(request, *args, **kwargs)


class ParticipanteDeclinarView(LoginRequiredMixin, RedirectView):
    """Declinar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("proyectos_usuario_list")

    def post(self, request, *args, **kwargs):
        proyecto_id = request.POST.get("proyecto_id")
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = get_object_or_404(
            ParticipanteProyecto,
            proyecto_id=proyecto_id,
            usuario=usuario_actual,
            tipo_participacion="invitado",
        )
        pp.tipo_participacion_id = "invitacion_rehusada"
        pp.save()

        messages.success(
            request,
            _(f"Ha rehusado ser participante del proyecto «{proyecto.titulo}»."),
        )
        return super().post(request, *args, **kwargs)


class ParticipanteDeleteView(LoginRequiredMixin, ChecksMixin, DeleteView):
    """Borra un registro de ParticipanteProyecto"""

    model = ParticipanteProyecto
    template_name = "participante-proyecto/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("proyecto_detail", args=[self.object.proyecto.id])

    def test_func(self):
        return self.es_coordinador(self.get_object().proyecto.id)


class ProyectoCreateView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Crea una nueva solicitud de proyecto"""

    model = Proyecto
    template_name = "proyecto/new.html"
    # fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]
    form_class = ProyectoForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed,
        # to do custom logic on form data. It should return an HttpResponse.
        proyecto = form.save()
        self._guardar_coordinador(proyecto)
        self._registrar_creacion(proyecto)
        return redirect("proyecto_detail", proyecto.id)

    def get_form(self, form_class=None):
        """
        Devuelve el formulario añadiendo automáticamente el campo Convocatoria,
        que es requerido.
        """
        form = super(ProyectoCreateView, self).get_form(form_class)
        form.instance.convocatoria = Convocatoria(date.today().year)
        return form

    def _guardar_coordinador(self, proyecto):
        # Los PIET debe solicitarlos uno de los coordinadores del estudio
        # ("coordinador principal") quien podrá nombrar a otro coordinador.
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

    def test_func(self):
        # TODO: Comprobar usuario para Proyectos de titulación y POU.
        # TODO: Comprobar fecha
        return self.es_pas_o_pdi()


class ProyectoDetailView(LoginRequiredMixin, ChecksMixin, DetailView):
    """Muestra una solicitud de proyecto."""

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
            self.object.participantes.filter(
                tipo_participacion__in=["invitado", "invitacion_rehusada"]
            )
            .order_by("tipo_participacion", "usuario__first_name", "usuario__last_name")
            .all()
        )
        context["invitados"] = invitados

        context["campos"] = json.loads(self.object.programa.campos)

        return context

    def test_func(self):
        # TODO: Los evaluadores y gestores también tendrán que tener acceso.
        return self.esta_vinculado(self.kwargs["pk"])


class ProyectoPresentarView(LoginRequiredMixin, ChecksMixin, RedirectView):
    """Presenta una solicitud de proyecto.

    El proyecto pasa de estado «Borrador» a estado «Solicitado».
    Se envían correos a los agentes involucrados.
    """

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("proyecto_detail", args=[kwargs.get("pk")])

    def post(self, request, *args, **kwargs):
        proyecto_id = kwargs.get("pk")
        proyecto = Proyecto.objects.get(pk=proyecto_id)

        # TODO ¿Chequear el estado actual del proyecto?
        if not proyecto.ayuda:
            messages.error(request, _("No ha indicado la ayuda solicitada."))
            return super().post(request, *args, **kwargs)

        if proyecto.ayuda > proyecto.programa.max_ayuda:
            messages.error(
                request,
                _(
                    f"La ayuda solicitada ({proyecto.ayuda} €) excede el máximo "
                    "permitido para este programa ({proyecto.programa.max_ayuda} €)."
                ),
            )
            return super().post(request, *args, **kwargs)

        if not proyecto.tiene_invitados():
            messages.error(
                request,
                _("La solicitud debe incluir al menos un invitado a participar."),
            )
            return super().post(request, *args, **kwargs)

        self._enviar_invitaciones(request, proyecto)
        if proyecto.programa.nombre_corto in ["PIEC", "PRACUZ"]:
            self._enviar_solicitudes_visto_bueno(request, proyecto)
        # TODO Enviar "resguardo" al solicitante. PDF?

        proyecto.estado = "SOLICITADO"
        proyecto.save()

        # TODO Modificar detail.html para no mostrar botones de edición/presentación
        messages.success(request, _("Su solicitud de proyecto ha sido presentada."))
        return super().post(request, *args, **kwargs)

    def _enviar_invitaciones(self, request, proyecto):
        """Envia un mensaje a cada uno de los invitados al proyecto."""
        for invitado in proyecto.participantes.filter(tipo_participacion="invitado"):
            send_templated_mail(
                template_name="invitacion",
                from_email=None,  # settings.DEFAULT_FROM_EMAIL
                recipient_list=[invitado.usuario.email],
                context={
                    "nombre_coordinador": request.user.get_full_name(),
                    "nombre_invitado": invitado.usuario.get_full_name(),
                    "sexo_invitado": invitado.usuario.sexo,
                    "titulo_proyecto": proyecto.titulo,
                    "programa_proyecto": f"{proyecto.programa.nombre_corto} "
                    + f"({proyecto.programa.nombre_largo})",
                    "descripcion_proyecto": proyecto.descripcion,
                    "site_url": settings.SITE_URL,
                },
            )

    def _enviar_solicitudes_visto_bueno(self, request, proyecto):
        """Envia un mensaje al responsable del centro solicitando su visto bueno."""
        send_templated_mail(
            template_name="solicitud_visto_bueno",
            from_email=None,  # settings.DEFAULT_FROM_EMAIL
            recipient_list=[proyecto.centro.email_decano],
            context={
                "nombre_coordinador": request.user.get_full_name(),
                "nombre_decano": proyecto.centro.nombre_decano,
                "tratamiento_decano": proyecto.centro.tratamiento_decano,
                "titulo_proyecto": proyecto.titulo,
                "programa_proyecto": f"{proyecto.programa.nombre_corto} "
                f"({proyecto.programa.nombre_largo})",
                "descripcion_proyecto": proyecto.descripcion,
                "site_url": settings.SITE_URL,
            },
        )

    def test_func(self):
        # TODO: Comprobar fecha
        return self.es_coordinador(self.kwargs["pk"])


class ProyectoUpdateFieldView(LoginRequiredMixin, ChecksMixin, UpdateView):
    """Actualiza un campo de una solicitud de proyecto."""

    # TODO: Comprobar estado/fecha
    model = Proyecto
    template_name = "proyecto/update.html"

    def get_form_class(self, **kwargs):
        campo = self.kwargs["campo"]
        if campo in (
            "centro",
            "codigo",
            "convocatoria",
            "estado",
            "estudio",
            "linea",
            "programa",
        ):
            raise Http404(_("No puede editar ese campo."))

        if campo not in ("titulo", "departamento", "licencia", "ayuda"):
            return modelform_factory(
                Proyecto, fields=(campo,), widgets={campo: SummernoteWidget()}
            )
        self.fields = (campo,)
        return super().get_form_class()

    def test_func(self):
        return self.es_coordinador(self.kwargs["pk"])


class ProyectosUsuarioView(LoginRequiredMixin, TemplateView):
    """Lista los proyectos a los que está vinculado el usuario actual."""

    template_name = "proyecto/mis-proyectos.html"

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        context = super().get_context_data(**kwargs)
        context["proyectos_coordinados"] = (
            Proyecto.objects.filter(
                participantes__usuario=usuario,
                participantes__tipo_participacion_id__in=[
                    "coordinador",
                    "coordinador_principal",
                ],
            )
            .order_by("programa__nombre_corto", "linea__nombre", "titulo")
            .all()
        )
        context["proyectos_participados"] = (
            Proyecto.objects.filter(
                participantes__usuario=usuario,
                participantes__tipo_participacion_id="participante",
            )
            .order_by("programa__nombre_corto", "linea__nombre", "titulo")
            .all()
        )
        context["proyectos_invitado"] = (
            Proyecto.objects.filter(
                participantes__usuario=usuario,
                participantes__tipo_participacion_id="invitado",
            )
            .order_by("programa__nombre_corto", "linea__nombre", "titulo")
            .all()
        )

        return context
