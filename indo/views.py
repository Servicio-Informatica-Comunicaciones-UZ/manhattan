# Standard library
from time import sleep
import csv
import json
import os

# import magic
from datetime import date

# from os.path import splitext

# Third-party
from annoying.functions import get_config, get_object_or_None
from django_summernote.widgets import SummernoteWidget
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableView
from social_django.utils import load_strategy
from templated_email import send_templated_mail

# Alternativa: Usar Headless Chromium con <https://github.com/pyppeteer/pyppeteer>
from weasyprint import HTML  # https://weasyprint.org/ - No soporta Javascript
import bleach
import pypandoc

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
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
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

# Local Django
from accounts.pipeline import get_identidad
from .filters import ProyectoCentroFilter, ProyectoFilter
from .forms import (
    AsignarCorrectorForm,
    CorreccionForm,
    CorrectorForm,
    EvaluadorForm,
    HaceConstarForm,
    InvitacionForm,
    MemoriaRespuestaForm,
    ProyectoFilterFormHelper,
    ProyectoForm,
    ResolucionForm,
)
from .models import (
    Centro,
    Convocatoria,
    Criterio,
    MemoriaRespuesta,
    # MemoriaSubapartado,
    ParticipanteProyecto,
    Plan,
    Proyecto,
    Resolucion,
    TipoParticipacion,
    Valoracion,
)
from .tables import (
    CorrectoresTable,
    EvaluadoresTable,
    EvaluacionProyectosTable,
    MemoriaProyectosTable,
    MemoriasAsignadasTable,
    ProyectosAceptadosTable,
    ProyectosCierreEconomicoTable,
    ProyectosEvaluadosTable,
    ProyectosTable,
    ProyectoCorrectorTable,
    ProyectoUPTable,
)
from .tasks import generar_pdf
from .utils import PagedFilteredTableView, registrar_evento


@permission_required('admin')
def actualizar_usuarios(request, anyo):
    """Actualiza los usuarios coordinadores con los datos de Gestión de Identidades."""
    proyectos = Proyecto.objects.filter(convocatoria__id=anyo)
    for proyecto in proyectos:
        print(f'Actualizando coordinador del proyecto: {proyecto.id}')
        coordinador = proyecto.coordinador

        try:
            get_identidad(load_strategy(request), None, coordinador)
        except Exception as ex:
            return HttpResponse(
                f'ERROR al actualizar el usuario «{coordinador.username}»'
                f' (proyecto {proyecto.id}): {ex}'
            )

    return HttpResponse('Coordinadores actualizados!')


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
            or self.es_evaluador_del_proyecto(proyecto_id)
            or usuario_actual.has_perm('indo.ver_proyecto')  # Gestores
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

    def es_corrector_del_proyecto(self, proyecto_id):
        """Devuelve si el usuario actual es corrector de la memoria del proyecto indicado."""
        self.permission_denied_message = _('Usted no es corrector de la memoria de este proyecto.')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        usuario_actual = self.request.user

        return usuario_actual == proyecto.corrector


class AyudaView(TemplateView):
    """Muestra la página de ayuda."""

    template_name = 'ayuda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = Convocatoria.get_ultima().id
        return context


class CorreccionVerView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Muestra la valoración de la memoria del proyecto indicado."""

    permission_required = 'indo.ver_memorias'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    model = Proyecto
    template_name = 'gestion/proyecto/correccion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'anyo': self.object.convocatoria.id,
                'url_anterior': self.request.headers.get('Referer', reverse('home')),
            }
        )
        return context


class MemoriaCorreccionUpdateView(LoginRequiredMixin, ChecksMixin, UpdateView):
    """Muestra y permite editar la corrección de la memoria un proyecto."""

    model = Proyecto
    template_name = 'corrector/correccion.html'
    form_class = CorreccionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context

    def get_success_url(self):
        return reverse('memorias_asignadas_table', kwargs={'anyo': self.object.convocatoria.id})

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        proyecto = self.object
        admision = self.request.POST.get('aceptacion_corrector')

        if admision == 'False':
            proyecto.estado = 'MEM_NO_ADMITIDA'
            registrar_evento(
                self.request, 'inadmision_memoria', 'No admisión de la memoria', proyecto
            )
        elif admision == 'True':
            proyecto.estado = 'MEM_ADMITIDA'
            registrar_evento(self.request, 'admision_memoria', 'Admisión de la memoria', proyecto)
        proyecto.save()

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        proyecto = self.get_object()
        self._enviar_notificacion(request, proyecto)

        return super().post(request, *args, **kwargs)

    def test_func(self):
        return self.es_corrector_del_proyecto(self.kwargs['pk'])

    def _enviar_notificacion(self, request, proyecto):
        """Envía un mensaje al coordinador del proyecto."""
        if request.POST.get('aceptacion_corrector') == 'True':
            plantilla = 'memoria_admitida'
        else:
            plantilla = 'memoria_no_admitida'

        try:
            send_templated_mail(
                template_name=plantilla,
                from_email=None,  # settings.DEFAULT_FROM_EMAIL
                recipient_list=(proyecto.coordinador.email,),
                context={
                    'proyecto': proyecto,
                    'coordinador': proyecto.coordinador,
                    'vicerrector': settings.VICERRECTOR.strip('"'),
                    'observaciones': request.POST.get('observaciones_corrector'),
                },
                cc=(settings.DEFAULT_FROM_EMAIL,),  # Enviar copia al vicerrectorado
            )
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request,
                _('No se envió por correo la notificación de admisión de la memoria: ' f'{err}'),
            )


class CorrectorTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra los usuarios del grupo Correctores y un formulario para añadir más."""

    permission_required = 'indo.gestionar_correctores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = CorrectoresTable
    template_name = 'gestion/corrector/tabla_correctores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'anyo': Convocatoria.get_ultima().id,
                'form': CorrectorForm(),
            }
        )
        return context

    def get_queryset(self):
        correctores = Group.objects.get(name='Correctores')
        return correctores.user_set.all()


class CorrectorAnyadirView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Añade un usuario al grupo Correctores."""

    permission_required = 'indo.gestionar_correctores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def post(self, request, *args, **kwargs):
        nip = request.POST.get('nip')

        # Comprobamos si el usuario ya existe en el sistema.
        # Si no existe previamente, lo creamos.
        User = get_user_model()
        usuario = get_object_or_None(User, username=nip)
        if not usuario:
            try:
                usuario = User.crear_usuario(request, nip)
            except Exception as ex:
                messages.error(request, 'ERROR: %s' % ex.args[0])
                return redirect('correctores_table')

        grupo_correctores = Group.objects.get(name='Correctores')
        grupo_correctores.user_set.add(usuario)
        messages.success(request, _('Se ha añadido al usuario como corrector.'))

        return redirect('correctores_table')


class CorrectorCesarView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Saca a un usuario del grupo Correctores."""

    permission_required = 'indo.gestionar_correctores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        usuario = get_object_or_None(User, pk=request.POST.get('user_id'))
        grupo_correctores = Group.objects.get(name='Correctores')
        grupo_correctores.user_set.remove(usuario)  # o usuario.groups.remove(grupo_correctores)
        messages.success(request, _('Se ha cesado al usuario como corrector.'))

        return redirect('correctores_table')


class EvaluacionVerView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Muestra la evaluación del proyecto indicado."""

    permission_required = 'indo.ver_evaluacion'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    template_name = 'gestion/evaluacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        context['anyo'] = proyecto.convocatoria.id
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

        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        context['anyo'] = proyecto.convocatoria.id
        context['proyecto'] = proyecto
        context['criterios'] = Criterio.objects.filter(
            convocatoria_id=proyecto.convocatoria_id
        ).all()
        context['dict_valoraciones'] = proyecto.get_dict_valoraciones()
        return context

    def post(self, request, *args, **kwargs):
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

        if not proyecto.esta_evaluado:
            proyecto.esta_evaluado = True
            proyecto.save()

        messages.success(
            request, _(f'Se ha guardado la evaluación del proyecto «{proyecto.titulo}».')
        )
        return redirect('proyectos_evaluados_table', proyecto.convocatoria_id)

    def test_func(self):
        return self.es_evaluador_del_proyecto(self.kwargs['pk'])


class MemoriasAsignadasTableView(LoginRequiredMixin, UserPassesTestMixin, SingleTableView):
    """Lista las memorias asignadas al usuario (corrector) actual."""

    permission_denied_message = _('Sólo los correctores pueden acceder a esta página.')
    table_class = MemoriasAsignadasTable
    template_name = 'corrector/mis_memorias.html'

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(corrector=self.request.user)
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )

    def test_func(self):
        return self.request.user.groups.filter(name='Correctores').exists()


class ProyectoAceptarView(LoginRequiredMixin, ChecksMixin, SuccessMessageMixin, UpdateView):
    """Aceptación por el coordinador de las condiciones concedidas para un proyecto."""

    fields = ('aceptacion_coordinador',)
    model = Proyecto
    success_message = _(
        'Se ha guardado su decisión sobre las condiciones concedidas '
        'para el proyecto «%(titulo)s».'
    )
    template_name = 'proyecto/aceptar_condiciones.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        proyecto = self.object
        aceptacion = self.request.POST.get('aceptacion_coordinador')

        if aceptacion == 'false':
            proyecto.estado = 'RECHAZADO'
            registrar_evento(
                self.request, 'rechazo_condiciones', 'Rechazo de las condiciones', proyecto
            )
        elif aceptacion == 'true':
            proyecto.estado = 'ACEPTADO'
            registrar_evento(
                self.request, 'aceptacion_condiciones', 'Aceptación de las condiciones', proyecto
            )
        proyecto.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, titulo=self.object.titulo)

    def get_success_url(self):
        return reverse_lazy('proyecto_detail', args=[self.object.id])

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        if proyecto.estado != 'APROBADO':
            self.permission_denied_message = _(
                f'''El estado actual del proyecto ({proyecto.get_estado_display()})
                no permite aceptar/rechazar las condiciones.'''
            )
            return False

        fecha_limite = proyecto.convocatoria.fecha_max_aceptacion_resolucion
        if not fecha_limite:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria la fecha para aceptar las condiciones.'
            )
            return False
        if date.today() > fecha_limite:
            fecha_limite_str = localize(fecha_limite)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                 para aceptar/rechazar las condiciones.'''
            )
            return False

        return self.es_coordinador(self.kwargs['pk'])


class ProyectoCorrectorTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra los proyectos aceptados por su coordinador y el corrector de memorias asignado."""

    permission_required = 'indo.asignar_correctores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = ProyectoCorrectorTable
    template_name = 'gestion/proyecto/tabla_correctores.html'

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectoCorrectorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Actualizar el corrector de la memoria de un proyecto."""

    permission_required = 'indo.asignar_correctores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    model = Proyecto
    template_name = 'gestion/proyecto/editar_corrector.html'
    form_class = AsignarCorrectorForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context

    def get_success_url(self):
        return reverse('proyecto_corrector_table', kwargs={'anyo': self.object.convocatoria.id})


class ProyectoEvaluadorTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra una tabla con las solicitudes de proyectos presentadas y el evaluador asignado."""

    permission_required = 'indo.listar_evaluadores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = EvaluadoresTable
    template_name = 'gestion/proyecto/tabla_evaluadores.html'

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
        # Las vinculaciones las crea la administrativa del Secretariado de Calidad
        # e Innovación Docente
        # <https://ayudica.unizar.es/otrs/public.pl?Action=PublicFAQZoom;ItemID=127>
        advertencia, nip_evaluadores = User.get_nips_vinculacion(60)
        if advertencia:
            messages.warning(request, advertencia)
        nip_evaluadores = [str(nip) for nip in nip_evaluadores]
        # XXX - Desarrollo
        # nip_evaluadores += ['136040', '327618', '329639', '370109', '408704', '181785']

        # Creamos los usuarios que no existan ya en la aplicación.
        evaluadores = Group.objects.get(name='Evaluadores')
        for nip in nip_evaluadores:
            usuario = get_object_or_None(User, username=nip)
            if not usuario:
                try:
                    usuario = User.crear_usuario(request, nip)
                except Exception as ex:
                    messages.error(request, 'ERROR: %s' % ex.args[0])
                    return redirect('evaluador_update')
            # Añadimos los usuarios al grupo Evaluadores.
            evaluadores.user_set.add(usuario)  # or usuario.groups.add(evaluadores)

        # Quitamos del grupo Evaluadores a los usuarios que ya no tengan esa vinculación.
        for usuario in evaluadores.user_set.all():
            if usuario.username not in nip_evaluadores:
                evaluadores.user_set.remove(usuario)  # or usuario.groups.remove(evaluadores)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context

    def get_success_url(self):
        return reverse('evaluadores_table', kwargs={'anyo': self.object.convocatoria.id})


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
            # Cuando se publica la resolución definitiva, La mayoría de los coordinadores ya han
            # aceptado las condiciones, y entonces no se debería retroceder al estado Aprobado.
            if proyecto.estado in ('SOLICITADO', 'DENEGADO'):
                proyecto.estado = 'APROBADO'
                registrar_evento(
                    self.request, 'aprobacion_proyecto', 'Aprobación del proyecto', proyecto
                )
        elif resolucion == 'false':
            proyecto.estado = 'DENEGADO'
            registrar_evento(
                self.request, 'denegacion_proyecto', 'Denegación del proyecto', proyecto
            )
        else:  # unknown
            proyecto.estado = 'SOLICITADO'
            registrar_evento(
                self.request,
                'anulacion_resolucion',
                'Anulación de la aprobación o denegación',
                proyecto,
            )
        proyecto.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, titulo=self.object.titulo)

    def get_success_url(self):
        return reverse_lazy('evaluaciones_table', args=[self.object.convocatoria_id])


class ProyectoUPTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra las unidades de planificación de los proyectos, y los gastos autorizados."""

    permission_required = 'indo.ver_up'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = ProyectoUPTable
    template_name = 'gestion/proyecto/tabla_up.html'

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .order_by(
                'programa__nombre_corto',
                'titulo',
            )
        )


class ProyectosUpCsvView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Muestra las unidades de planificación de los proyectos, y los gastos autorizados."""

    permission_required = 'indo.ver_up'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def get(self, request, *args, **kwargs):
        datos_proyectos = Proyecto.get_up_gastos(kwargs.get('anyo'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="proyectos_up_gastos.csv"'
        writer = csv.writer(response)
        writer.writerows(datos_proyectos)
        return response


class HomePageView(TemplateView):
    """Muestra la página principal."""

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = Convocatoria.get_ultima().id
        return context


class InvitacionView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Muestra un formulario para invitar a una persona a un proyecto determinado."""

    form_class = InvitacionForm
    model = ParticipanteProyecto
    template_name = 'participante-proyecto/invitar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['proyecto_id'])
        context.update(
            {
                'anyo': proyecto.convocatoria.id,
                'proyecto': proyecto,
            }
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Update the kwargs for the form init method with ours
        kwargs.update(self.kwargs)  # self.kwargs contains all URL conf params
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('proyecto_detail', kwargs={'pk': self.kwargs['proyecto_id']})

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['proyecto_id'])
        fecha_limite = proyecto.convocatoria.fecha_max_aceptos
        if not fecha_limite:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria la fecha límite'
                ' para aceptar participar en un proyecto.'
            )
            return False
        if date.today() > fecha_limite:
            fecha_limite_str = localize(fecha_limite)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                para que los invitados puedan aceptar participar en el proyecto.'''
            )
            return False

        return self.es_coordinador(self.kwargs['proyecto_id']) or self.request.user.has_perm(
            'indo.editar_proyecto'
        )


class ParticipanteAceptarView(LoginRequiredMixin, RedirectView):
    """Aceptar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        proyecto = get_object_or_404(Proyecto, pk=kwargs.get('proyecto_id'))
        return reverse_lazy('mis_proyectos', kwargs={'anyo': proyecto.convocatoria_id})

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

        if proyecto.estado in ('BORRADOR', 'ANULADO', 'DENEGADO'):
            messages.error(
                request,
                _(
                    f'''El estado actual del proyecto ({proyecto.get_estado_display()})
                    no permite aceptar invitaciones a participar en él.'''
                ),
            )
            return super().post(request, *args, **kwargs)

        fecha_limite = proyecto.convocatoria.fecha_max_aceptos
        if not fecha_limite:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria la fecha límite'
                ' para que los invitados puedan aceptar participar en un proyecto.'
            )
            return False
        if date.today() > fecha_limite:
            fecha_limite_str = localize(fecha_limite)
            messages.error(
                request,
                _(
                    f'''Se ha superado la fecha límite ({fecha_limite_str})
                    para que los invitados puedan aceptar participar en el proyecto.'''
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


class ParticipanteAnyadirView(LoginRequiredMixin, ChecksMixin, TemplateView):
    """Muestra un formulario para añadir excepcionalmente un participante a un proyecto."""

    template_name = 'participante-proyecto/anyadir_excepcional.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(Proyecto, pk=kwargs['proyecto_id'])
        context.update(
            {
                'anyo': proyecto.convocatoria.id,
                'proyecto': proyecto,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        proyecto = get_object_or_404(Proyecto, pk=kwargs['proyecto_id'])
        # Obtenemos el usuario (si ya existe en el sistema).
        nip = request.POST.get('nip')
        User = get_user_model()
        usuario = get_object_or_None(User, username=nip)

        if not usuario:
            # El usuario no existe previamente. Lo creamos con los datos de Gestión de Identidades.
            try:
                usuario = User.crear_usuario(request, nip)
            except Exception as ex:
                messages.error(request, 'ERROR: %s' % ex.args[0])
                return redirect('participante_anyadir', proyecto.id)
        else:
            # El usuario existe. Actualizamos sus datos con los de Gestión de Identidades.
            try:
                usuario.actualizar(self.request)
            except Exception as ex:
                # Si Identidades devuelve un error, finalizamos mostrando el mensaje de error.
                messages.error(request, f'ERROR: {ex}')
                return redirect('participante_anyadir', proyecto.id)

        # Si el usuario no está activo, finalizamos explicando esta circunstancia.
        if not usuario.is_active:
            texto = mark_safe(
                _(
                    '''Usuario inactivo en el sistema de Gestión de Identidades.<br>
                    Solicite en Ayudica que se le asigne la vinculación
                    «Participantes externos Proyectos Innovación Docente».'''
                )
            )
            messages.error(request, f'ERROR: {texto}')
            return redirect('participante_anyadir', proyecto.id)

        # Comprobamos que el usuario no esté ya en el número máximo de equipos permitido.
        num_equipos = usuario.get_num_equipos(proyecto.convocatoria_id)
        num_max_equipos = proyecto.convocatoria.num_max_equipos
        if num_equipos >= num_max_equipos:
            messages.error(
                request,
                _(
                    f'''No puede añadir este usuario porque ya forma parte
                    del número máximo de equipos de trabajo permitido ({num_max_equipos}).'''
                ),
            )
            return redirect('participante_anyadir', proyecto.id)

        # Añadimos al usuario como participante del proyecto.
        participante = ParticipanteProyecto(
            proyecto=proyecto,
            tipo_participacion=TipoParticipacion('participante'),
            usuario=usuario,
        )
        participante.save()

        # Quitamos al usuario de invitado, si lo estaba.
        invitado = proyecto.participantes.filter(
            usuario=usuario, tipo_participacion='invitado'
        ).first()
        if invitado:
            invitado.delete()

        messages.success(request, _('Se ha añadido al usuario al equipo de trabajo del proyecto.'))
        return redirect('proyecto_detail', proyecto.id)

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['proyecto_id'])
        fecha_limite = proyecto.convocatoria.fecha_max_modificacion_equipos
        if not fecha_limite:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria la fecha límite'
                ' para modificar excepcionalmente los equipos de trabajo.'
            )
            return False
        if date.today() > fecha_limite:
            fecha_limite_str = localize(fecha_limite)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str}) para
                las modificaciones excepcionales del equipo de trabajo de un proyecto.'''
            )
            return False

        return self.request.user.has_perm('indo.editar_proyecto')


class ParticipanteDeclinarView(LoginRequiredMixin, RedirectView):
    """Declinar la invitación a participar en un proyecto."""

    def get_redirect_url(self, *args, **kwargs):
        proyecto = get_object_or_404(Proyecto, pk=self.request.POST.get('proyecto_id'))
        return reverse_lazy('mis_proyectos', kwargs={'anyo': proyecto.convocatoria_id})

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
        proyecto = get_object_or_404(Proyecto, pk=self.request.POST.get('proyecto_id'))
        return reverse_lazy('mis_proyectos', kwargs={'anyo': proyecto.convocatoria_id})

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.proyecto.convocatoria.id
        return context

    def get_success_url(self):
        return reverse_lazy('proyecto_detail', args=[self.object.proyecto.id])

    def test_func(self):
        return self.es_coordinador(self.get_object().proyecto.id) or self.request.user.has_perm(
            'indo.editar_proyecto'
        )


class ParticipanteHaceConstarView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Generar PDF de constancia de participación de proyectos de una persona"""

    permission_required = 'indo.hace_constar'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página')
    template_name = 'participante-proyecto/form_hace_constar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'anyo': Convocatoria.get_ultima().id,
                'form': HaceConstarForm(),
                'url_anterior': self.request.headers.get('Referer', reverse('home')),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        nip = request.POST.get('nip')
        email = request.POST.get('email')
        convocatoria = Convocatoria.get_ultima()

        User = get_user_model()
        if nip:
            usuario = get_object_or_None(User, username=nip)
        elif email:
            usuario = get_object_or_None(User, email=email)
        else:
            messages.error(request, _('Debe introducir un NIP o una dirección de e-mail.'))
            return super().get(request, *args, **kwargs)

        if not usuario:
            messages.error(request, _('No se ha encontrado ese usuario.'))
            return super().get(request, *args, **kwargs)

        proyectos_participados = (
            Proyecto.objects.filter(convocatoria__id=convocatoria.id)
            .filter(
                participantes__usuario=usuario,
                aceptacion_comision=True,
                aceptacion_coordinador=True,
                participantes__tipo_participacion_id__in=['participante', 'coordinador'],
            )
            .order_by('titulo')
            .all()
        )

        contexto = {
            'vicerrector': settings.VICERRECTOR.strip('"'),
            'usuario': usuario,
            'proyecto_list': proyectos_participados,
            'convocatoria': convocatoria,
        }

        documento_html = HTML(
            string=render_to_string(
                'participante-proyecto/hace_constar.html', context=contexto, request=request
            ),
            # En la plantilla, las URL de los CSS y las imágenes son relativas.
            # Al usar `HTML(string=...)` WeasyPrint no sabe cuál es la URL base, hay que dársela.
            base_url=request.build_absolute_uri(),
        )
        response = HttpResponse(content_type='application/pdf')
        musername = usuario.email.split('@')[0]
        response['Content-Disposition'] = f'attachment; filename="hace_constar_{musername}.pdf"'
        documento_html.write_pdf(response)
        return response


class ProyectosCierreEconomicoTableView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleTableView
):
    """Muestra los proyectos aceptados y su cierre económico."""

    permission_required = 'indo.ver_economico'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = ProyectosCierreEconomicoTable
    template_name = 'gestion/proyecto/tabla_cierre_economico.html'

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .order_by(
                '-aceptacion_corrector',
                '-aceptacion_economico',
                'programa__nombre_corto',
                'linea__nombre',
                'titulo',
            )
        )


class ProyectoCreateView(LoginRequiredMixin, ChecksMixin, CreateView):
    """Crea una nueva solicitud de proyecto"""

    model = Proyecto
    template_name = 'proyecto/new.html'
    form_class = ProyectoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = Convocatoria.get_ultima().id
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed,
        # to do custom logic on form data. It should return an HttpResponse.
        proyecto = form.save()
        self._guardar_coordinador(proyecto)
        registrar_evento(
            self.request, 'creacion_solicitud', 'Creacion inicial de la solicitud', proyecto
        )
        return redirect('proyecto_detail', proyecto.id)

    def get_form(self, form_class=None):
        """
        Devuelve el formulario añadiendo automáticamente el campo Convocatoria,
        que es requerido, y el usuario, para comprobar si tiene los permisos necesarios.
        """
        form = super().get_form(form_class)
        form.instance.user = self.request.user
        form.instance.convocatoria = Convocatoria.get_ultima()
        return form

    def _guardar_coordinador(self, proyecto):
        pp = ParticipanteProyecto(
            proyecto=proyecto,
            tipo_participacion=TipoParticipacion(nombre='coordinador'),
            usuario=self.request.user,
        )
        pp.save()

    def test_func(self):
        convocatoria = Convocatoria.get_ultima()
        fecha_minima = convocatoria.fecha_min_solicitudes
        if not fecha_minima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria la fecha'
                ' en que se abre el plazo para presentar solicitudes.'
            )
            return False
        if date.today() < fecha_minima:
            fecha_limite_str = localize(fecha_minima)
            self.permission_denied_message = _(
                f'''El plazo de solicitudes se abrirá el {fecha_limite_str}.'''
            )
            return False

        fecha_maxima = convocatoria.fecha_max_solicitudes
        if not fecha_maxima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria'
                ' la fecha límite para presentar solicitudes.'
            )
            return False
        if date.today() > fecha_maxima:
            fecha_limite_str = localize(fecha_maxima)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                 para presentar solicitudes.'''
            )
            return False

        return self.es_pas_o_pdi()


class ProyectoAnularView(LoginRequiredMixin, ChecksMixin, RedirectView):
    """Cambia el estado de una solicitud de proyecto a Anulada."""

    model = Proyecto

    def get_redirect_url(self, *args, **kwargs):
        proyecto = Proyecto.objects.get(pk=kwargs.get('pk'))
        return reverse('mis_proyectos', kwargs={'anyo': proyecto.convocatoria_id})

    def post(self, request, *args, **kwargs):
        proyecto = Proyecto.objects.get(pk=kwargs.get('pk'))
        proyecto.estado = 'ANULADO'
        proyecto.save()

        messages.success(request, _('Su solicitud de proyecto ha sido anulada.'))
        registrar_evento(
            self.request, 'anulacion_solicitud', 'Anulación de la solicitud', proyecto
        )
        return super().post(request, *args, **kwargs)

    def test_func(self):
        return self.es_coordinador(self.kwargs['pk'])


class MemoriaDetailView(LoginRequiredMixin, ChecksMixin, TemplateView):
    """Muestra la memoria del proyecto indicado."""

    template_name = 'memoria/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        context['anyo'] = proyecto.convocatoria.id
        context['proyecto'] = proyecto
        context['apartados'] = proyecto.convocatoria.apartados_memoria.all()
        context['dict_respuestas'] = proyecto.get_dict_respuestas_memoria()

        context['permitir_edicion'] = self.es_coordinador(proyecto.id) and proyecto.estado in (
            'ACEPTADO',
            'MEM_NO_ADMITIDA',
        )
        context['url_anterior'] = self.request.headers.get('Referer', reverse('home'))

        return context

    """
    def post(self, request, *args, **kwargs):
        proyecto = get_object_or_404(Proyecto, pk=kwargs['pk'])
        subapartados = MemoriaSubapartado.objects.filter(
            apartado__convocatoria_id=proyecto.convocatoria_id
        ).all()
        dict_respuestas = proyecto.get_dict_respuestas_memoria()

        for subapartado in subapartados:
            respuesta = dict_respuestas.get(subapartado.id)
            if not respuesta:
                respuesta = MemoriaRespuesta(
                    proyecto_id=proyecto.id, subapartado_id=subapartado.id
                )

            if subapartado.tipo == 'texto':
                respuesta.texto = request.POST.get(str(subapartado.id))
            elif subapartado.tipo == 'fichero':
                fichero = request.FILES.get('fichero')

                if fichero:
                    ext = splitext(fichero.name)[1].lower()
                    if ext != '.pdf':
                        raise ValidationError(_('El fichero debe tener extensión .pdf .'))

                    filetype = magic.from_buffer(fichero.read(2048), mime=True)
                    fichero.seek(0)
                    if 'pdf' not in filetype:  # application/pdf, x-pdf, x-bzpdf, x-gzpdf
                        raise ValidationError(_('El fichero no es un PDF.'))
                    # fichero.name = f'{proyecto.id}.pdf'

                    respuesta.fichero = fichero

            respuesta.save()

        messages.success(
            request, _(f'Se ha guardado la memoria del proyecto «{proyecto.titulo}».')
        )
        return redirect('proyecto_detail', proyecto.id)
    """

    def test_func(self):
        return (
            self.es_coordinador(self.kwargs['pk'])
            or self.es_corrector_del_proyecto(self.kwargs['pk'])
            or self.request.user.has_perm('indo.ver_memorias')
        )


class MemoriaPresentarView(LoginRequiredMixin, ChecksMixin, RedirectView):
    """Presenta la memoria final de proyecto.

    El proyecto pasa de estado «Aceptado» a estado «Memoria presentada».
    Se genera (en segundo plano) un documento PDF que podrá archivarse en Zaguán.
    """

    def create_context(self, proyecto):
        return {
            'anyo': proyecto.convocatoria.id,
            'proyecto': proyecto,
            'apartados': proyecto.convocatoria.apartados_memoria.all(),
            'dict_respuestas': proyecto.get_dict_respuestas_memoria(),
        }

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('proyecto_detail', args=[kwargs.get('pk')])

    def post(self, request, *args, **kwargs):
        proyecto_id = kwargs.get('pk')
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

        proyecto.estado = 'MEM_PRESENTADA'
        # Si la memoria ya había sido valorada por el corrector, rechazada, y se está subsanando:
        proyecto.aceptacion_corrector = None
        proyecto.es_publicable = None
        proyecto.save()

        contexto = self.create_context(proyecto)
        # base_url = request.build_absolute_uri().removesuffix('presentar/')  # Requiere Python 3.9
        base_url = request.build_absolute_uri()[: -len('presentar/')]
        documento_html = HTML(
            string=render_to_string('memoria/detail.html', context=contexto, request=request),
            # En la plantilla, las URL de los CSS y las imágenes son relativas.
            # Al usar `HTML(string=...)` WeasyPrint no sabe cuál es la URL base, hay que dársela.
            base_url=base_url,
        )

        # Generar ruta tipo `BASE_DIR/media/2021/PIIDUZ_42.pdf`
        pdf_destino = os.path.join(
            settings.MEDIA_ROOT,
            'memoria',
            str(proyecto.convocatoria_id),
            f'{proyecto.programa.nombre_corto}_{proyecto_id}.pdf',
        )

        generar_pdf(documento_html, pdf_destino)  # Proceso lento, lo ejecutamos en segundo plano.

        messages.success(
            request, _('La memoria de su proyecto ha sido presentada para su corrección.')
        )
        registrar_evento(
            self.request, 'presentacion_memoria', 'Presentacion de la memoria', proyecto
        )
        return super().post(request, *args, **kwargs)

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs.get('pk'))
        if proyecto.estado not in ('ACEPTADO', 'MEM_NO_ADMITIDA'):
            self.permission_denied_message = _(
                f'''El estado actual del proyecto ({proyecto.get_estado_display()})
                no permite modificar la memoria.'''
            )
            return False

        fecha_maxima = proyecto.convocatoria.fecha_max_memorias
        if not fecha_maxima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria'
                ' la fecha límite para presentar memorias.'
            )
            return False
        if date.today() > fecha_maxima:
            fecha_limite_str = localize(fecha_maxima)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                 para presentar memorias.'''
            )
            return False

        return self.es_coordinador(self.kwargs['pk'])


class MemoriaUpdateFieldView(LoginRequiredMixin, ChecksMixin, UpdateView):
    """Actualiza la respuesta a un subapartado de una memoria."""

    model = MemoriaRespuesta
    template_name = 'memoria/update.html'
    form_class = MemoriaRespuestaForm  # Definido en `forms.py`

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.proyecto.convocatoria.id
        return context

    def get_object(self, queryset=None):
        """Return the object the view is displaying."""
        proyecto_id = self.kwargs.get('proyecto_id')
        subapartado_id = self.kwargs.get('sub_pk')
        return MemoriaRespuesta.get_or_create(proyecto_id, subapartado_id)

    def get_success_url(self):
        return reverse_lazy('memoria_detail', args=[self.object.proyecto_id])

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs.get('proyecto_id'))
        fecha_maxima = proyecto.convocatoria.fecha_max_memorias
        if not fecha_maxima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria'
                ' la fecha límite para presentar memorias.'
            )
            return False
        if date.today() > fecha_maxima:
            fecha_limite_str = localize(fecha_maxima)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                 para presentar memorias.'''
            )
            return False

        return self.es_coordinador(self.kwargs['proyecto_id']) or self.request.user.has_perm(
            'indo.editar_proyecto'
        )


class ProyectoDetailView(LoginRequiredMixin, ChecksMixin, DetailView):
    """Muestra una solicitud de proyecto."""

    model = Proyecto
    template_name = 'proyecto/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['anyo'] = self.object.convocatoria.id

        context['participantes'] = (
            self.object.participantes.filter(tipo_participacion='participante')
            .order_by('usuario__first_name', 'usuario__last_name')
            .all()
        )

        context['invitados'] = (
            self.object.participantes.filter(
                tipo_participacion__in=['invitado', 'invitacion_rehusada']
            )
            .order_by('tipo_participacion', 'usuario__first_name', 'usuario__last_name')
            .all()
        )

        context['campos'] = json.loads(self.object.programa.campos)

        context['permitir_edicion'] = (
            self.es_coordinador(self.object.id) and self.object.en_borrador()
        ) or self.request.user.has_perm('indo.editar_proyecto')

        context['permitir_anyadir_sin_invitacion'] = self.request.user.has_perm(
            'indo.editar_proyecto'
        ) and (
            self.object.convocatoria.fecha_max_aceptos
            < date.today()
            < self.object.convocatoria.fecha_max_modificacion_equipos
        )

        # No mostrar si la Comisión ha aprobado o no el proyecto
        # hasta que se publique la resolución.
        if (
            self.object.estado in ('DENEGADO', 'APROBADO')
            and not self.object.convocatoria.notificada_resolucion_provisional
        ):
            context['object'].estado = 'SOLICITADO'

        context['es_coordinador'] = self.es_coordinador(self.object.id)

        context['url_anterior'] = self.request.headers.get('Referer', reverse('home'))

        return context

    def test_func(self):
        proyecto_id = self.kwargs['pk']
        return self.esta_vinculado_o_es_decano_o_es_coordinador(proyecto_id)


class ProyectosCsvView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Devuelve un fichero CSV con datos de todos los proyectos introducidos en el año."""

    permission_required = 'indo.listar_evaluadores'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def get(self, request, *args, **kwargs):
        datos_proyectos = Proyecto.get_todos(kwargs.get('anyo'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="proyectos.csv"'
        writer = csv.writer(response)
        writer.writerows(datos_proyectos)
        return response


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

    def get(self, request, *args, **kwargs):
        convocatoria = get_object_or_404(Convocatoria, pk=self.kwargs.get('anyo'))

        hitos = ('fecha_max_aceptacion_resolucion', 'fecha_max_alegaciones')
        for hito in hitos:
            if not getattr(convocatoria, hito):
                fecha_faltante = convocatoria._meta.get_field(hito).verbose_name
                messages.warning(
                    request,
                    _(
                        f'Recuerde introducir en la convocatoria la {fecha_faltante}'
                        ' desde el menú Gestión → Administrar convocatorias.'
                    ),
                )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['convocatoria'] = get_object_or_404(Convocatoria, pk=self.kwargs.get('anyo'))
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .exclude(estado__in=['BORRADOR', 'ANULADO'])
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectoFichaView(DetailView):
    """Muestra una ficha con la información básica del proyecto."""

    model = Proyecto
    template_name = 'proyecto/ficha.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = self.object.convocatoria.id
        return context


class ProyectoMemoriasTableView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    """Muestra los proyectos aceptados y enlaces a su memoria y dictamen del corrector."""

    permission_required = 'indo.ver_memorias'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = MemoriaProyectosTable
    template_name = 'gestion/proyecto/tabla_memorias.html'

    def get(self, request, *args, **kwargs):
        convocatoria = Convocatoria.objects.get(id=self.kwargs.get('anyo'))

        hitos = ('fecha_max_memorias', 'fecha_max_gastos')
        for hito in hitos:
            if not getattr(convocatoria, hito):
                fecha_faltante = convocatoria._meta.get_field(hito).verbose_name
                messages.warning(
                    request,
                    _(
                        f'Recuerde introducir en la convocatoria la {fecha_faltante}'
                        ' desde el menú Gestión → Administrar convocatorias.'
                    ),
                )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectosNotificarView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    """Envía a los coordinadores de los proyectos la resolución de la Comisión de Evaluación"""

    permission_required = 'indo.listar_evaluaciones'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('evaluaciones_table', kwargs={'anyo': kwargs.get('anyo')})

    def post(self, request, *args, **kwargs):
        convocatoria = Convocatoria.objects.get(id=self.kwargs.get('anyo'))
        if not convocatoria.notificada_resolucion_provisional:
            proyectos_con_dotacion = (
                Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
                .filter(aceptacion_comision=True, ayuda_provisional__gt=0)
                .all()
            )
            proyectos_sin_dotacion = (
                Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
                .filter(aceptacion_comision=True, ayuda_provisional=0)
                .all()
            )
            variante = '_provisional'
        else:
            proyectos_con_dotacion = (
                Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
                .filter(aceptacion_comision=True, ayuda_definitiva__gt=0)
                .all()
            )
            proyectos_sin_dotacion = (
                Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
                .filter(aceptacion_comision=True, ayuda_definitiva=0)
                .all()
            )
            variante = '_definitiva'

        try:
            for proyecto in proyectos_con_dotacion:
                self._enviar_notificaciones(proyecto, 'notificacion_con_dotacion' + variante)
                sleep(0.1)  # El servidor SMTP tiene un control de flujo de 600 mensajes por minuto
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request,
                _(
                    'No se enviaron por correo las notificaciones de la resolución '
                    f'a los proyectos con dotación: {err}'
                ),
            )

        try:
            for proyecto in proyectos_sin_dotacion:
                self._enviar_notificaciones(proyecto, 'notificacion_sin_dotacion' + variante)
                sleep(0.1)  # El servidor SMTP tiene un control de flujo de 600 mensajes por minuto
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request,
                _(
                    'No se enviaron por correo las notificaciones de la resolución '
                    f'a los proyectos sin dotación: {err}'
                ),
            )

        if variante == '_provisional':
            convocatoria.notificada_resolucion_provisional = True
        else:
            convocatoria.notificada_resolucion_definitiva = True
        convocatoria.save()

        messages.success(request, _('Se han enviado las notificaciones.'))
        return super().post(request, *args, **kwargs)

    def _enviar_notificaciones(self, proyecto, plantilla):
        # emails_coordinadores = [c.email for c in proyecto.get_coordinadores()]
        # gestores = Group.objects.get(name='Gestores').user_set.all()
        # emails_gestores = [gestor.email for gestor in gestores]
        send_templated_mail(
            template_name=plantilla,
            from_email=None,  # settings.DEFAULT_FROM_EMAIL
            recipient_list=(proyecto.coordinador.email,),
            context={
                'proyecto': proyecto,
                'coordinador': proyecto.coordinador,
                'site_url': settings.SITE_URL,
                'vicerrector': settings.VICERRECTOR.strip('"'),
            },
            cc=(settings.DEFAULT_FROM_EMAIL,),  # Enviar copia al vicerrectorado
        )


class ProyectoTableView(LoginRequiredMixin, PermissionRequiredMixin, PagedFilteredTableView):
    """Muestra una tabla de todos los proyectos introducidos en una convocatoria."""

    filter_class = ProyectoFilter
    formhelper_class = ProyectoFilterFormHelper
    model = Proyecto
    permission_required = 'indo.listar_proyectos'
    permission_denied_message = _('Sólo los gestores pueden acceder a esta página.')
    table_class = ProyectosTable
    template_name = 'gestion/proyecto/tabla_proyectos.html'

    def get(self, request, *args, **kwargs):
        convocatoria = Convocatoria.objects.get(id=self.kwargs.get('anyo'))

        hitos = (
            'fecha_min_solicitudes',
            'fecha_max_solicitudes',
            'fecha_max_aceptos',
            'fecha_max_visto_buenos',
        )
        for hito in hitos:
            if not getattr(convocatoria, hito):
                fecha_faltante = convocatoria._meta.get_field(hito).verbose_name
                messages.warning(
                    request,
                    _(
                        f'Recuerde introducir en la convocatoria la {fecha_faltante}'
                        ' en el menú Gestión → Administrar convocatorias.'
                    ),
                )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            # .exclude(estado__in=['BORRADOR', 'ANULADO'])
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

        # if not proyecto.tiene_invitados():
        if not (proyecto.tiene_invitados() or proyecto.tiene_participantes()):
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

        messages.success(request, _('Su solicitud de proyecto ha sido presentada.'))
        registrar_evento(
            self.request, 'presentacion_solicitud', 'Presentación de la solicitud', proyecto
        )
        return super().post(request, *args, **kwargs)

    def _enviar_invitaciones(self, request, proyecto):
        """Envía un mensaje a cada uno de los invitados al proyecto."""
        try:
            for invitado in proyecto.participantes.filter(tipo_participacion='invitado'):
                send_templated_mail(
                    template_name='invitacion',
                    from_email=None,  # settings.DEFAULT_FROM_EMAIL
                    recipient_list=[invitado.usuario.email],
                    context={
                        'nombre_coordinador': request.user.full_name,
                        'nombre_invitado': invitado.usuario.full_name,
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
                sleep(0.1)  # Tiene que pasar un mínimo de 100ms entre un mensaje y el siguiente
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request,
                _(
                    'No se enviaron por correo las invitaciones a participar en el proyecto: '
                    f'{err}'
                ),
            )

    def _enviar_solicitudes_visto_bueno_centro(self, request, proyecto):
        """Envía un mensaje al responsable del centro solicitando su visto bueno."""
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

        try:
            send_templated_mail(
                template_name='solicitud_visto_bueno_centro',
                from_email=None,  # settings.DEFAULT_FROM_EMAIL
                recipient_list=[proyecto.centro.email_decano],
                context={
                    'nombre_coordinador': request.user.full_name,
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
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request, _(f'No se envió por correo la solicitud de Visto Bueno del centro: {err}')
            )

    def _is_email_valid(self, email):
        """Validate email address"""
        try:
            validate_email(email)
        except ValidationError:
            return False
        return True

    def _enviar_solicitudes_visto_bueno_estudio(self, request, proyecto):
        """Envía mensaje a los coordinadores del plan solicitando su visto bueno."""
        email_coordinadores_estudio = [
            f'{p.email_coordinador}'
            for p in proyecto.estudio.planes.all()
            if self._is_email_valid(p.email_coordinador)
        ]

        try:
            send_templated_mail(
                template_name='solicitud_visto_bueno_estudio',
                from_email=None,  # settings.DEFAULT_FROM_EMAIL
                recipient_list=email_coordinadores_estudio,
                context={
                    'nombre_coordinador': request.user.full_name,
                    'titulo_proyecto': proyecto.titulo,
                    'programa_proyecto': f'{proyecto.programa.nombre_corto} '
                    f'({proyecto.programa.nombre_largo})',
                    'descripcion_proyecto': pypandoc.convert_text(
                        proyecto.descripcion, 'md', format='html'
                    ).replace('\\\n', '\n'),
                    'site_url': settings.SITE_URL,
                },
            )
        except Exception as err:  # smtplib.SMTPAuthenticationError etc
            messages.warning(
                request,
                _(f'No se envió por correo la solicitud de Visto Bueno del estudio: {err}'),
            )

    def test_func(self):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])

        if proyecto.estado != 'BORRADOR':
            self.permission_denied_message = _(
                f'''El estado actual del proyecto ({proyecto.get_estado_display()})
                no permite presentar la solicitud.'''
            )
            return False

        fecha_minima = proyecto.convocatoria.fecha_min_solicitudes
        if not fecha_minima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria'
                ' la fecha en que se abre el plazo para presentar solicitudes.'
            )
            return False
        if date.today() < fecha_minima:
            fecha_limite_str = localize(fecha_minima)
            self.permission_denied_message = _(
                f'''El plazo de solicitudes se abrirá el {fecha_limite_str}.'''
            )
            return False

        fecha_maxima = proyecto.convocatoria.fecha_max_solicitudes
        if not fecha_maxima:
            self.permission_denied_message = _(
                'No se ha establecido en la convocatoria'
                ' la fecha límite para presentar solicitudes.'
            )
            return False
        if date.today() > fecha_maxima:
            fecha_limite_str = localize(fecha_maxima)
            self.permission_denied_message = _(
                f'''Se ha superado la fecha límite ({fecha_limite_str})
                 para presentar solicitudes.'''
            )
            return False

        return self.es_coordinador(self.kwargs['pk'])


class ProyectoUpdateFieldView(LoginRequiredMixin, ChecksMixin, UpdateView):
    """Actualiza un campo de una solicitud de proyecto."""

    model = Proyecto
    template_name = 'proyecto/update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'anyo': self.object.convocatoria.id,
                'campo': self.kwargs['campo'],
                'url_anterior': self.request.headers.get('Referer', reverse('home')),
            }
        )
        return context

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
            'aceptacion_economico',
            'id_uxxi',
        ):
            # Salvo para los campos anteriores, usamos una caja de texto enriquecido
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

                # Si se excede la longitud del campo, `cleaned_data` es `{}`, y `texto` es `None`,
                # lo que provoca una excepción al llamar a `bleach.clean(texto)`.
                if texto is None:
                    texto = ''

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

        if campo == 'ayuda':
            self.fields = (campo,)
            formulario = super().get_form_class()

            def clean(self):
                cleaned_data = super(formulario, self).clean()
                ayuda_solicitada = cleaned_data.get('ayuda')
                if (
                    ayuda_solicitada > 0
                    and self.instance.coordinador.get_colectivo_principal() == 'ADS'
                ):
                    self.add_error(
                        'ayuda',
                        _(
                            'El profesorado de centros adscritos no puede ser '
                            'destinatario de cuantías económicas.'
                        ),
                    )
                return cleaned_data

            formulario.clean = clean
            return formulario

        self.fields = (campo,)
        return super().get_form_class()

    def get_success_url(self):
        if self.kwargs['campo'] in ('visto_bueno_centro', 'visto_bueno_estudio'):
            return reverse_lazy('mis_proyectos', kwargs={'anyo': self.object.convocatoria_id})
        if self.kwargs['campo'] == 'aceptacion_economico':
            return reverse_lazy(
                'cierre_economico_table', kwargs={'anyo': self.get_object().convocatoria_id}
            )
        if self.kwargs['campo'] == 'id_uxxi':
            return reverse_lazy('up_table', kwargs={'anyo': self.object.convocatoria_id})
        return super().get_success_url()

    def test_func(self):
        """Devuelve si el usuario está autorizado a modificar este campo."""
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])

        if (
            self.kwargs['campo'] == 'visto_bueno_centro'
            and self.es_decano_o_director(self.kwargs['pk'])
        ) or (
            self.kwargs['campo'] == 'visto_bueno_estudio'
            and self.es_coordinador_estudio(self.kwargs['pk'])
        ):
            fecha_limite = proyecto.convocatoria.fecha_max_visto_buenos
            if not fecha_limite:
                self.permission_denied_message = _(
                    'No se ha establecido en la convocatoria'
                    ' la fecha límite para dar los Visto Bueno.'
                )
                return False
            if date.today() > fecha_limite:
                fecha_limite_str = localize(fecha_limite)
                self.permission_denied_message = _(
                    f'''Se ha superado la fecha límite ({fecha_limite_str})
                    para dar el visto bueno.'''
                )
                return False

            return True

        if self.es_coordinador(self.kwargs['pk']):
            permitidos_coordinador = (
                'titulo',
                'descripcion',
                'ayuda',
                'financiacion',
                # Campos listados en `indo_programa`
                'actividades',
                'afectadas',
                'ambito',
                'aplicacion',
                'caracter_estrategico',
                'contenido_modulos',
                'contenidos',
                'contexto',
                'contexto_aplicacion',
                'continuidad',
                'duracion',
                'enlace',
                'formatos',
                'idioma',
                'impacto',
                'indicadores',
                'innovacion',
                'interes',
                'justificacion_equipo',
                'material_previo',
                'mejoras',
                'metodos',
                'metodos_estudio',
                'multimedia',
                'objetivos',
                'proyectos_anteriores',
                'ramas',
                'seminario',
                'tecnologias',
                'tipo',
            )
            if not self.kwargs['campo'] in permitidos_coordinador:
                self.permission_denied_message = _('No puede modificar este campo.')
                return False

            if not proyecto.en_borrador():
                self.permission_denied_message = _(
                    f'''El estado actual del proyecto ({proyecto.get_estado_display()})
                    no permite modificar los campos de la solicitud.'''
                )
                return False

            return True

        return self.request.user.has_perm('indo.editar_proyecto')


class ProyectoVerCondicionesView(LoginRequiredMixin, ChecksMixin, TemplateView):
    """Muestra las condiciones aceptadas/rechazadas por el coordinador de un proyecto"""

    template_name = 'proyecto/aceptar_condiciones.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        context.update(
            {
                'anyo': proyecto.convocatoria.id,
                'proyecto': proyecto,
            }
        )
        return context

    def test_func(self):
        return self.es_coordinador(self.kwargs['pk'])


class ProyectosAceptadosCentrosListView(ListView):
    model = Centro
    template_name = 'proyecto/centros_list.html'

    def get_queryset(self):
        centro_ids = (
            Proyecto.objects.filter(convocatoria_id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .values_list('centro_id', flat=True)
            .order_by('centro_id')
            .distinct()
            .all()
        )
        return Centro.objects.filter(id__in=centro_ids).order_by('academico_id_nk')


class ProyectosAceptadosTableView(ExportMixin, PagedFilteredTableView):
    """Lista los proyectos aceptados en una convocatoria, con su centro."""

    filter_class = ProyectoCentroFilter
    model = Proyecto
    table_class = ProyectosAceptadosTable
    template_name = 'proyecto/aceptados.html'
    export_name = 'proyectos_aceptados'
    exclude_columns = ('vinculo',)  # En el CSV mostrar el título sin el enlace

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        academico_id_nk = self.request.GET.get('centro__academico_id_nk', None)
        if academico_id_nk:
            context['centro'] = get_object_or_404(Centro, academico_id_nk=academico_id_nk)
        return context

    def get_queryset(self):
        return (
            Proyecto.objects.filter(convocatoria__id=self.kwargs['anyo'])
            .filter(aceptacion_coordinador=True)
            .order_by('programa__nombre_corto', 'linea__nombre', 'titulo')
        )


class ProyectosUsuarioView(LoginRequiredMixin, TemplateView):
    """Lista los proyectos a los que está vinculado el usuario actual."""

    template_name = 'proyecto/mis-proyectos.html'

    def get(self, request, *args, **kwargs):
        # `LOGIN_URL` usa el año actual, pero la convocatoria sale a mitad de año
        convocatoria = get_object_or_None(Convocatoria, pk=kwargs['anyo'])
        if not convocatoria:
            ultima_convo = Convocatoria.get_ultima()
            return redirect('mis_proyectos', ultima_convo.id)
        return super().get(request, *args, **kwargs)

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
            .exclude(estado__in=['BORRADOR', 'ANULADO', 'DENEGADO'])
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
            id_estudios_coordinados = {p.estudio_id for p in planes_coordinados}
            context['proyectos_estudios_coordinados'] = Proyecto.objects.filter(
                convocatoria_id=anyo,
                programa__requiere_visto_bueno_estudio=True,
                estudio_id__in=id_estudios_coordinados,
            )

        return context


class ResolucionListView(ListView):
    """Lista las resoluciones publicadas en el tablón de anuncios."""

    model = Resolucion
    template_name = 'resolucion/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anyo'] = Convocatoria.get_ultima().id
        return context
