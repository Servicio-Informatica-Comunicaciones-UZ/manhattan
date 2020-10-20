# Standard library
import csv
import json
from datetime import date

# Third-party
from annoying.functions import get_config, get_object_or_None
from django_summernote.widgets import SummernoteWidget
from django_tables2.views import SingleTableView
from templated_email import send_templated_mail
import bleach
import pypandoc

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

# Local Django
from .forms import EvaluadorForm, InvitacionForm, ProyectoForm, ResolucionForm
from .models import (
    Centro,
    Convocatoria,
    Criterio,
    Evento,
    ParticipanteProyecto,
    Plan,
    Proyecto,
    Registro,
    TipoParticipacion,
    Valoracion,
)
from .tables import (
    EvaluadoresTable,
    EvaluacionProyectosTable,
    ProyectosEvaluadosTable,
    ProyectosTable,
)


class ChecksMixin(UserPassesTestMixin):
    """Proporciona comprobaciones para autorizar o no una acción a un usuario."""

    def es_coordinador(self, proyecto_id):
        """Devuelve si el usuario actual es coordinador del proyecto indicado."""
        self.permission_denied_message = _('Usted no es coordinador de este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        coordinadores_participantes = proyecto.participantes.filter(
            tipo_participacion__in=['coordinador', 'coordinador_2']
        ).all()
        usuarios_coordinadores = list(map(lambda p: p.usuario, coordinadores_participantes))

        return usuario_actual in usuarios_coordinadores

    def es_participante(self, proyecto_id):
        """Devuelve si el usuario actual es participante del proyecto indicado."""
        self.permission_denied_message = _('Usted no es participante de este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = proyecto.participantes.filter(
            usuario=usuario_actual, tipo_participacion='participante'
        ).all()

        return True if pp else False

    def es_invitado(self, proyecto_id):
        """Devuelve si el usuario actual es invitado del proyecto indicado."""
        self.permission_denied_message = _('Usted no está invitado a este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = proyecto.participantes.filter(
            usuario=usuario_actual, tipo_participacion='invitado'
        ).all()

        return True if pp else False

    def esta_vinculado(self, proyecto_id):
        """Devuelve si el usuario actual está vinculado al proyecto indicado."""
        self.permission_denied_message = _('Usted no está vinculado a este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = (
            proyecto.participantes.filter(usuario=usuario_actual)
            .exclude(tipo_participacion='invitacion_rehusada')
            .all()
        )

        return True if pp else False

    def es_pas_o_pdi(self):
        """Devuelve si el usuario actual es PAS o PDI de la UZ o de sus centros adscritos."""
        self.permission_denied_message = _('Usted no es PAS ni PDI.')
        usuario_actual = self.request.user
        colectivos_del_usuario = json.loads(usuario_actual.colectivos)

        return any(
            col_autorizado in colectivos_del_usuario for col_autorizado in ['PAS', 'ADS', 'PDI']
        )

    def es_decano_o_director(self, proyecto_id):
        """Devuelve si el usuario actual es decano/director del centro del proyecto."""
        self.permission_denied_message = _('Usted no es decano/director del centro del proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        centro = proyecto.centro
        if not centro:
            return False

        nip_decano = centro.nip_decano
        return usuario_actual.username == str(nip_decano)

    def esta_vinculado_o_es_decano_o_es_coordinador(self, proyecto_id):
        """
        Devuelve si el usuario actual está vinculado al proyecto indicado
        o es decano o director del centro del proyecto
        o es coordinador del plan de estudios del proyecto."""
        self.permission_denied_message = _(
            'Usted no está vinculado a este proyecto, '
            'ni es decano/director del centro del proyecto, '
            'ni es coordinador del plan de estudios del proyecto.'
        )
        usuario_actual = self.request.user
        esta_autorizado = (
            self.esta_vinculado(proyecto_id)
            or self.es_decano_o_director(proyecto_id)
            or self.es_coordinador_estudio(proyecto_id)
            or usuario_actual.has_perm('indo.ver_proyecto')  # Gestores y evaluadores
        )

        return esta_autorizado

    def es_coordinador_estudio(self, proyecto_id):
        """Devuelve si el usuario actual es coordinador del estudio del proyecto."""
        self.permission_denied_message = _(
            'Usted no es coordinador del plan de estudios del proyecto.'
        )
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        estudio = proyecto.estudio
        if not estudio:
            return False

        nip_coordinadores = [
            f'{p.nip_coordinador}' for p in estudio.planes.all() if p.nip_coordinador
        ]
        return usuario_actual.username in nip_coordinadores

    def es_evaluador_del_proyecto(self, proyecto_id):
        """Devuelve si el usuario actual es evaluador del proyecto indicado."""
        self.permission_denied_message = _('Usted no es evaluador de este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user

        return usuario_actual == proyecto.evaluador


class AyudaView(TemplateView):
    template_name = 'ayuda.html'


class EvaluacionVerView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Muestra la evaluación del proyecto indicado."""

    permission_required = 'indo.ver_evaluacion'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    template_name = 'gestion/evaluacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = get_object_or_404(Proyecto, pk=kwargs['pk'])
        context['proyecto'] = proyecto
        context['criterios'] = Criterio.objects.filter(
            convocatoria_id=proyecto.convocatoria_id
        ).all()
        context['dict_valoraciones'] = proyecto.get_dict_valoraciones()
        return context


class EvaluacionView(LoginRequiredMixin, ChecksMixin, TemplateView):
    """Muestra y permite editar las valoraciones de un proyecto."""

    template_name = 'evaluador/evaluacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = get_object_or_404(Proyecto, pk=kwargs['pk'])
        context['proyecto'] = proyecto
        context['criterios'] = Criterio.objects.filter(
            convocatoria_id=proyecto.convocatoria_id
        ).all()
        context['dict_valoraciones'] = proyecto.get_dict_valoraciones()
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = get_object_or_404(Proyecto, pk=kwargs['pk'])
        criterios = Criterio.objects.filter(convocatoria_id=proyecto.convocatoria_id).all()
        dict_valoraciones = proyecto.get_dict_valoraciones()

        for criterio in criterios:
            valoracion = dict_valoraciones.get(criterio.id)
            if not valoracion:
                valoracion = Valoracion(proyecto_id=proyecto.id, criterio_id=criterio.id)

            if criterio.tipo == 'opcion':
                valoracion.opcion_id = request.POST.get(str(criterio.id))
            elif criterio.tipo == 'texto':
                valoracion.texto = request.POST.get(str(criterio.id))
            valoracion.save()

        messages.success(
            request, _(f'Se ha guardado la evaluación del proyecto «{proyecto.titulo}».')
        )
        return redirect('proyectos_evaluados_table', proyecto.convocatoria_id)

    def test_func(self):
        return self.es_evaluador_del_proyecto(self.kwargs['pk'])


class ProyectoEvaluadorTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra una tabla con las solicitudes de proyectos presentadas y el evaluador asignado."""

    permission_required = 'indo.listar_evaluadores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = EvaluadoresTable
    template_name = 'gestion/proyecto/tabla_evaluadores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.kwargs['anyo']
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .exclude(estado__in=['BORRADOR', 'ANULADO'])
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectosEvaluadosTableView(LoginRequiredMixin, UserPassesTestMixin, SingleTableView):
    """Lista los proyectos asignados al usuario (evaluador) actual."""

    permission_denied_message = _('Sólo los evaluadores pueden acceder a esta página.')
    table_class = ProyectosEvaluadosTable
    template_name = 'evaluador/mis_proyectos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.kwargs['anyo']
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(evaluador=self.request.user)
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )

    def test_func(self):
        return self.request.user.groups.filter(name='Evaluadores').exists()


class ProyectoEvaluadorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Actualizar el evaluador de un proyecto."""

    permission_required = 'indo.editar_evaluador'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    model = Proyecto
    template_name = 'gestion/proyecto/editar_evaluador.html'
    form_class = EvaluadorForm

    def get(self, request, *args, **kwargs):
        User = get_user_model()
        # Obtenemos los NIPs de los usuarios con vinculación «Evaluador externo innovacion ACPUA».
        advertencia, nip_evaluadores = User.get_nips_vinculacion(60)
        if advertencia:
            messages.warning(request, advertencia)
        nip_evaluadores = [str(nip) for nip in nip_evaluadores]
        # nip_evaluadores = ['136040', '327618', '329639', '370109']  # XXX - Desarrollo

        # Creamos los usuarios que no existan ya en la aplicación.
        evaluadores = Group.objects.get(name='Evaluadores')
        for nip in nip_evaluadores:
            usuario = get_object_or_None(User, username=nip)
            if not usuario:
                usuario = User.crear_usuario(request, nip)
            # Añadimos los usuarios al grupo Evaluadores.
            evaluadores.user_set.add(usuario)  # or usuario.groups.add(evaluadores)

        # Quitamos del grupo Evaluadores a los usuarios que ya no tengan esa vinculación.
        for usuario in evaluadores.user_set.all():
            if usuario.username not in nip_evaluadores:
                evaluadores.user_set.remove(usuario)  # or usuario.groups.remove(evaluadores)

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('evaluadores_table', kwargs={'anyo': self.object.convocatoria})


class ProyectoResolucionUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView
):
    """Actualizar la resolución de la Comisión Evaluadora sobre un proyecto."""

    permission_required = 'indo.editar_resolucion'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    model = Proyecto
    success_message = _(
        'Se ha guardado la resolución de la comisión sobre el proyecto «%(titulo)s».'
    )
    template_name = 'gestion/proyecto/editar_resolucion.html'
    form_class = ResolucionForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        proyecto = self.object
        resolucion = self.request.POST.get('aceptacion_comision')

        if resolucion == 'true':
            proyecto.estado = 'APROBADO'
        elif resolucion == 'false':
            proyecto.estado = 'DENEGADO'
        else:  # unknown
            proyecto.estado = 'SOLICITADO'
        proyecto.save()

        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, titulo=self.object.titulo)

    def get_success_url(self):
        return reverse_lazy('evaluaciones_table', args=[self.object.convocatoria_id])


class HomePageView(TemplateView):
    template_name = 'home.html'


class InvitacionView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Muestra un formulario para invitar a una persona a un proyecto determinado."""

    form_class = InvitacionForm
    model = ParticipanteProyecto
    template_name = 'participante-proyecto/invitar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto_id = self.kwargs['proyecto_id']
        context['proyecto'] = Proyecto.objects.get(id=proyecto_id)
        return context

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        # Update the kwargs for the form init method with ours
        kwargs.update(self.kwargs)  # self.kwargs contains all URL conf params
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('proyecto_detail', kwargs={'pk': self.kwargs['proyecto_id']})

    def test_func(self):
        # TODO: Comprobar estado del proyecto, fecha.
        return self.es_coordinador(self.kwargs['proyecto_id']) or self.request.user.has_perm(
            'indo.editar_proyecto'
        )


class ParticipanteAceptarView(LoginRequiredMixin, RedirectView):
    """Aceptar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mis_proyectos', kwargs={'anyo': date.today().year})

    def post(self, request, *args, **kwargs):
        usuario_actual = self.request.user
        proyecto_id = kwargs.get('proyecto_id')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

        num_equipos = usuario_actual.get_num_equipos(proyecto.convocatoria_id)
        num_max_equipos = proyecto.convocatoria.num_max_equipos
        if num_equipos >= num_max_equipos:
            messages.error(
                request,
                _(
                    f'''No puede aceptar esta invitación porque ya forma parte del número
                máximo de equipos de trabajo permitido ({num_max_equipos}).
                Para poder aceptar esta invitación, antes debería renunciar a participar
                en algún otro proyecto.'''
                ),
            )
            return super().post(request, *args, **kwargs)

        pp = get_object_or_404(
            ParticipanteProyecto,
            proyecto_id=proyecto_id,
            usuario=usuario_actual,
            tipo_participacion='invitado',
        )
        pp.tipo_participacion_id = 'participante'
        pp.save()

        messages.success(
            request, _(f'Ha pasado a ser participante del proyecto «{proyecto.titulo}».')
        )
        return super().post(request, *args, **kwargs)


class ParticipanteDeclinarView(LoginRequiredMixin, RedirectView):
    """Declinar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mis_proyectos', kwargs={'anyo': date.today().year})

    def post(self, request, *args, **kwargs):
        proyecto_id = request.POST.get('proyecto_id')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = get_object_or_404(
            ParticipanteProyecto,
            proyecto_id=proyecto_id,
            usuario=usuario_actual,
            tipo_participacion='invitado',
        )
        pp.tipo_participacion_id = 'invitacion_rehusada'
        pp.save()

        messages.success(
            request, _(f'Ha rehusado ser participante del proyecto «{proyecto.titulo}».')
        )
        return super().post(request, *args, **kwargs)


class ParticipanteRenunciarView(LoginRequiredMixin, RedirectView):
    """Renunciar a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mis_proyectos', kwargs={'anyo': date.today().year})

    def post(self, request, *args, **kwargs):
        proyecto_id = request.POST.get('proyecto_id')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user
        pp = get_object_or_404(
            ParticipanteProyecto,
            proyecto_id=proyecto_id,
            usuario=usuario_actual,
            tipo_participacion='participante',
        )
        pp.tipo_participacion_id = 'invitacion_rehusada'
        pp.save()

        messages.success(
            request, _(f'Ha renunciado a participar en el proyecto «{proyecto.titulo}».')
        )
        return super().post(request, *args, **kwargs)


class ParticipanteDeleteView(LoginRequiredMixin, ChecksMixin, DeleteView):
    """Borra un registro de ParticipanteProyecto"""

    model = ParticipanteProyecto
    template_name = 'participante-proyecto/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('proyecto_detail', args=[self.object.proyecto.id])

    def test_func(self):
        return self.es_coordinador(self.get_object().proyecto.id) or self.request.user.has_perm(
            'indo.editar_proyecto'
        )


class ProyectoCreateView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Crea una nueva solicitud de proyecto"""

    model = Proyecto
    template_name = 'proyecto/new.html'
    form_class = ProyectoForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed,
        # to do custom logic on form data. It should return an HttpResponse.
        proyecto = form.save()
        self._guardar_coordinador(proyecto)
        self._registrar_creacion(proyecto)
        return redirect('proyecto_detail', proyecto.id)

    def get_form(self, form_class=None):
        """
        Devuelve el formulario añadiendo automáticamente el campo Convocatoria,
        que es requerido, y el usuario, para comprobar si tiene los permisos necesarios.
        """
        form = super(ProyectoCreateView, self).get_form(form_class)
        form.instance.user = self.request.user
        form.instance.convocatoria = Convocatoria(date.today().year)
        return form

    def _guardar_coordinador(self, proyecto):
        pp = ParticipanteProyecto(
            proyecto=proyecto,
            tipo_participacion=TipoParticipacion(nombre='coordinador'),
            usuario=self.request.user,
        )
        pp.save()

    def _registrar_creacion(self, proyecto):
        evento = Evento.objects.get(nombre='creacion_solicitud')
        registro = Registro(
            descripcion='Creación inicial de la solicitud', evento=evento, proyecto=proyecto
        )
        registro.save()

    def test_func(self):
        # TODO: Comprobar usuario para Proyectos de titulación y POU.
        # TODO: Comprobar fecha
        return self.es_pas_o_pdi()


class ProyectoAnularView(LoginRequiredMixin, ChecksMixin, RedirectView):
    """Cambia el estado de una solicitud de proyecto a Anulada."""

    model = Proyecto

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('mis_proyectos', kwargs={'anyo': date.today().year})

    def post(self, request, *args, **kwargs):
        proyecto = Proyecto.objects.get(pk=kwargs.get('pk'))
        proyecto.estado = 'ANULADO'
        proyecto.save()

        messages.success(request, _('Su solicitud de proyecto ha sido anulada.'))
        return super().post(request, *args, **kwargs)

    def test_func(self):
        return self.es_coordinador(self.kwargs['pk'])


class ProyectoDetailView(LoginRequiredMixin, ChecksMixin, DetailView):
    """Muestra una solicitud de proyecto."""

    model = Proyecto
    template_name = 'proyecto/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pp_coordinador = self.object.get_participante_or_none('coordinador')
        context['pp_coordinador'] = pp_coordinador

        pp_coordinador_2 = self.object.get_participante_or_none('coordinador_2')
        context['pp_coordinador_2'] = pp_coordinador_2

        participantes = (
            self.object.participantes.filter(tipo_participacion='participante')
            .order_by('usuario__first_name', 'usuario__last_name')
            .all()
        )
        context['participantes'] = participantes

        invitados = (
            self.object.participantes.filter(
                tipo_participacion__in=['invitado', 'invitacion_rehusada']
            )
            .order_by('tipo_participacion', 'usuario__first_name', 'usuario__last_name')
            .all()
        )
        context['invitados'] = invitados

        context['campos'] = json.loads(self.object.programa.campos)

        context['permitir_edicion'] = (
            self.es_coordinador(self.object.id) and self.object.en_borrador()
        ) or self.request.user.has_perm('indo.editar_proyecto')

        context['es_coordinador'] = (
            self.es_coordinador(self.object.id) and self.object.en_borrador()
        )

        return context

    def test_func(self):
        proyecto_id = self.kwargs['pk']
        return self.esta_vinculado_o_es_decano_o_es_coordinador(proyecto_id)


class ProyectoEvaluacionesCsvView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Devuelve un fichero CSV con las valoraciones de todos los proyectos presentados."""

    permission_required = 'indo.listar_evaluaciones'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def get(self, request, *args, **kwargs):
        valoraciones = Valoracion.get_todas(kwargs.get('anyo'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="valoraciones.csv"'
        writer = csv.writer(response)
        writer.writerows(valoraciones)
        return response


class ProyectoEvaluacionesTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra los proyectos presentados y enlaces a su evaluación y resolución de la Comisión."""

    permission_required = 'indo.listar_evaluaciones'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = EvaluacionProyectosTable
    template_name = 'gestion/proyecto/tabla_evaluaciones.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.kwargs['anyo']
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .exclude(estado__in=['BORRADOR', 'ANULADO'])
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectosNotificarView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    """Envía a los coordinadores de los proyectos la resolución de la Comisión de Evaluación"""

    permission_required = 'indo.listar_evaluaciones'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('evaluaciones_table', kwargs={'anyo': kwargs.get('anyo')})

    def post(self, request, *args, **kwargs):
        proyectos_con_dotacion = (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_comision=True, ayuda_concedida__gt=0)
            .all()
        )
        for proyecto in proyectos_con_dotacion:
            self._enviar_notificaciones(proyecto, 'notificacion_con_dotacion')

        proyectos_sin_dotacion = (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_comision=True, ayuda_concedida=0)
            .all()
        )
        for proyecto in proyectos_sin_dotacion:
            self._enviar_notificaciones(proyecto, 'notificacion_sin_dotacion')

        messages.success(request, _('Se han enviado las notificaciones.'))
        return super().post(request, *args, **kwargs)

    def _enviar_notificaciones(self, proyecto, plantilla):
        emails_coordinadores = [c.email for c in proyecto.get_coordinadores()]
        # gestores = Group.objects.get(name='Gestores').user_set.all()
        # emails_gestores = [gestor.email for gestor in gestores]
        send_templated_mail(
            template_name=plantilla,
            from_email=None,  # settings.DEFAULT_FROM_EMAIL
            recipient_list=emails_coordinadores,  # TODO: Añadir Cc
            context={
                'proyecto': proyecto,
                'coordinador': proyecto.get_coordinador(),
                'coordinador_2': proyecto.get_coordinador_2(),
                'site_url': settings.SITE_URL,
                'vicerrector': settings.VICERRECTOR,
            },
            cc=(settings.DEFAULT_FROM_EMAIL,),
        )


class ProyectoTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra una tabla de todos los proyectos presentados en una convocatoria."""

    permission_required = 'indo.listar_proyectos'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = ProyectosTable
    template_name = 'gestion/proyecto/tabla_proyectos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.kwargs['anyo']
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .exclude(estado__in=['BORRADOR', 'ANULADO'])
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectoPresentarView(LoginRequiredMixin, ChecksMixin, RedirectView):
    """Presenta una solicitud de proyecto.

    El proyecto pasa de estado «Borrador» a estado «Solicitado».
    Se envían correos a los agentes involucrados.
    """

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('proyecto_detail', args=[kwargs.get('pk')])

    def post(self, request, *args, **kwargs):
        proyecto_id = kwargs.get('pk')
        proyecto = Proyecto.objects.get(pk=proyecto_id)

        # TODO ¿Chequear el estado actual del proyecto?

        num_equipos = self.request.user.get_num_equipos(proyecto.convocatoria_id)
        num_max_equipos = proyecto.convocatoria.num_max_equipos
        if num_equipos >= num_max_equipos:
            messages.error(
                request,
                _(
                    f'''No puede presentar esta solicitud porque ya forma parte
                    del número máximo de equipos de trabajo permitido ({num_max_equipos}).
                    Para poder presentar esta solicitud de proyecto, antes debería renunciar
                    a participar en algún otro proyecto.'''
                ),
            )
            return super().post(request, *args, **kwargs)

        if request.user.get_colectivo_principal() == 'ADS' and proyecto.ayuda != 0:
            messages.error(
                request,
                _(
                    'Los profesores de los centros adscritos no pueden coordinar '
                    'proyectos con financiación.'
                ),
            )
            return super().post(request, *args, **kwargs)

        if proyecto.ayuda > proyecto.programa.max_ayuda:
            messages.error(
                request,
                _(
                    f'La ayuda solicitada ({proyecto.ayuda} €) excede el máximo '
                    f'permitido para este programa ({proyecto.programa.max_ayuda} €).'
                ),
            )
            return super().post(request, *args, **kwargs)

        if not proyecto.tiene_invitados():
            messages.error(
                request, _('La solicitud debe incluir al menos un invitado a participar.')
            )
            return super().post(request, *args, **kwargs)

        self._enviar_invitaciones(request, proyecto)

        if proyecto.programa.requiere_visto_bueno_centro:
            self._enviar_solicitudes_visto_bueno_centro(request, proyecto)

        if proyecto.programa.requiere_visto_bueno_estudio:
            self._enviar_solicitudes_visto_bueno_estudio(request, proyecto)

        # TODO Enviar "resguardo" al solicitante. PDF?

        proyecto.estado = 'SOLICITADO'
        proyecto.save()

        # TODO Modificar detail.html para no mostrar botones de edición/presentación
        messages.success(request, _('Su solicitud de proyecto ha sido presentada.'))
        return super().post(request, *args, **kwargs)

    def _enviar_invitaciones(self, request, proyecto):
        """Envia un mensaje a cada uno de los invitados al proyecto."""
        for invitado in proyecto.participantes.filter(tipo_participacion='invitado'):
            send_templated_mail(
                template_name='invitacion',
                from_email=None,  # settings.DEFAULT_FROM_EMAIL
                recipient_list=[invitado.usuario.email],
                context={
                    'nombre_coordinador': request.user.get_full_name(),
                    'nombre_invitado': invitado.usuario.get_full_name(),
                    'sexo_invitado': invitado.usuario.sexo,
                    'titulo_proyecto': proyecto.titulo,
                    'programa_proyecto': f'{proyecto.programa.nombre_corto} '
                    + f'({proyecto.programa.nombre_largo})',
                    'descripcion_proyecto': pypandoc.convert_text(
                        proyecto.descripcion, 'md', format='html'
                    ).replace('\\\n', '  \n'),
                    'site_url': settings.SITE_URL,
                },
            )

    def _enviar_solicitudes_visto_bueno_centro(self, request, proyecto):
        """Envia un mensaje al responsable del centro solicitando su visto bueno."""
        try:
            validate_email(proyecto.centro.email_decano)
        except ValidationError:
            messages.warning(
                request,
                _(
                    'La dirección de correo electrónico del director o decano '
                    'del centro no es válida.'
                ),
            )
            return

        send_templated_mail(
            template_name='solicitud_visto_bueno_centro',
            from_email=None,  # settings.DEFAULT_FROM_EMAIL
            recipient_list=[proyecto.centro.email_decano],
            context={
                'nombre_coordinador': request.user.get_full_name(),
                'nombre_decano': proyecto.centro.nombre_decano,
                'tratamiento_decano': proyecto.centro.tratamiento_decano,
                'titulo_proyecto': proyecto.titulo,
                'programa_proyecto': f'{proyecto.programa.nombre_corto} '
                f'({proyecto.programa.nombre_largo})',
                'descripcion_proyecto': pypandoc.convert_text(
                    proyecto.descripcion, 'md', format='html'
                ).replace('\\\n', '\n'),
                'site_url': settings.SITE_URL,
            },
        )

    def _is_email_valid(self, email):
        """Validate email address"""
        try:
            validate_email(email)
        except ValidationError:
            return False
        return True

    def _enviar_solicitudes_visto_bueno_estudio(self, request, proyecto):
        """Envia mensaje a los coordinadores del plan solicitando su visto bueno."""
        email_coordinadores_estudio = [
            f'{p.email_coordinador}'
            for p in proyecto.estudio.planes.all()
            if self._is_email_valid(p.email_coordinador)
        ]

        send_templated_mail(
            template_name='solicitud_visto_bueno_estudio',
            from_email=None,  # settings.DEFAULT_FROM_EMAIL
            recipient_list=email_coordinadores_estudio,
            context={
                'nombre_coordinador': request.user.get_full_name(),
                'titulo_proyecto': proyecto.titulo,
                'programa_proyecto': f'{proyecto.programa.nombre_corto} '
                f'({proyecto.programa.nombre_largo})',
                'descripcion_proyecto': pypandoc.convert_text(
                    proyecto.descripcion, 'md', format='html'
                ).replace('\\\n', '\n'),
                'site_url': settings.SITE_URL,
            },
        )

    def test_func(self):
        # TODO: Comprobar fecha
        return self.es_coordinador(self.kwargs['pk'])


class ProyectoUpdateFieldView(LoginRequiredMixin, ChecksMixin, UpdateView):
    """Actualiza un campo de una solicitud de proyecto."""

    # TODO: Comprobar estado/fecha
    model = Proyecto
    template_name = 'proyecto/update.html'

    def get_form_class(self, **kwargs):
        campo = self.kwargs['campo']
        if campo in ('centro', 'codigo', 'convocatoria', 'estado', 'estudio', 'linea', 'programa'):
            raise Http404(_('No puede editar ese campo.'))

        if campo not in (
            'titulo',
            'departamento',
            'licencia',
            'ayuda',
            'visto_bueno_centro',
            'visto_bueno_estudio',
        ):
            formulario = modelform_factory(
                Proyecto, fields=(campo,), widgets={campo: SummernoteWidget()}
            )

            def as_p(self):
                """
                Return this form rendered as HTML <p>s,
                with the helptext over the textarea.
                """
                return self._html_output(
                    normal_row='''<p%(html_class_attr)s>
                    %(label)s
                    %(help_text)s
                    %(field)s
                    </p>''',
                    error_row='%s',
                    row_ender='</p>',
                    help_text_html='<span class="helptext">%s</span>',
                    errors_on_separate_row=True,
                )

            formulario.as_p = as_p

            def clean(self):
                cleaned_data = super(formulario, self).clean()
                texto = cleaned_data.get(campo)
                # See <https://bleach.readthedocs.io/en/latest/clean.html>
                cleaned_data[campo] = mark_safe(
                    bleach.clean(
                        texto,
                        tags=(
                            bleach.sanitizer.ALLOWED_TAGS + get_config('ADDITIONAL_ALLOWED_TAGS')
                        ),
                        attributes=get_config('ALLOWED_ATTRIBUTES'),
                        styles=get_config('ALLOWED_STYLES'),
                        protocols=get_config('ALLOWED_PROTOCOLS'),
                        strip=True,
                    )
                )
                return cleaned_data

            formulario.clean = clean

            return formulario
        self.fields = (campo,)
        return super().get_form_class()

    def test_func(self):
        """Devuelve si el usuario está autorizado a modificar este campo."""
        return (
            self.es_coordinador(self.kwargs['pk'])
            or (
                self.kwargs['campo'] == 'visto_bueno_centro'
                and self.es_decano_o_director(self.kwargs['pk'])
            )
            or (
                self.kwargs['campo'] == 'visto_bueno_estudio'
                and self.es_coordinador_estudio(self.kwargs['pk'])
            )
            or self.request.user.has_perm('indo.editar_proyecto')
        )


class ProyectosUsuarioView(LoginRequiredMixin, TemplateView):
    """Lista los proyectos a los que está vinculado el usuario actual."""

    template_name = 'proyecto/mis-proyectos.html'

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        anyo = self.kwargs['anyo']
        context = super().get_context_data(**kwargs)
        context['proyectos_coordinados'] = (
            Proyecto.objects.filter(
                convocatoria__id=anyo,
                participantes__usuario=usuario,
                participantes__tipo_participacion_id__in=['coordinador', 'coordinador_2'],
            )
            .exclude(estado='ANULADO')
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
            .all()
        )
        context['proyectos_participados'] = (
            Proyecto.objects.filter(
                convocatoria__id=anyo,
                participantes__usuario=usuario,
                participantes__tipo_participacion_id='participante',
            )
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
            .all()
        )
        context['proyectos_invitado'] = (
            Proyecto.objects.filter(
                convocatoria__id=anyo,
                participantes__usuario=usuario,
                participantes__tipo_participacion_id='invitado',
            )
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
            .all()
        )

        try:
            nip_usuario = int(usuario.username)
        except ValueError:
            nip_usuario = 0

        centros_dirigidos = Centro.objects.filter(nip_decano=nip_usuario).all()
        if centros_dirigidos:
            context['proyectos_centros_dirigidos'] = Proyecto.objects.filter(
                convocatoria_id=anyo,
                programa__requiere_visto_bueno_centro=True,
                centro__in=centros_dirigidos,
            ).all()

        planes_coordinados = Plan.objects.filter(nip_coordinador=nip_usuario).all()
        if planes_coordinados:
            id_estudios_coordinados = set([p.estudio_id for p in planes_coordinados])
            context['proyectos_estudios_coordinados'] = Proyecto.objects.filter(
                convocatoria_id=anyo,
                programa__requiere_visto_bueno_estudio=True,
                estudio_id__in=id_estudios_coordinados,
            )

        return context
