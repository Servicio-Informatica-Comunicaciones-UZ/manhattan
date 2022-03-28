# Standard library
from datetime import date

# Third-party
from crispy_forms.bootstrap import InlineField, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Fieldset, Layout, Submit
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

# Django
from django import forms
from django.contrib.auth.models import Group
from django.db.models import BLANK_CHOICE_DASH
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Local Django
from accounts.models import CustomUser
from accounts.pipeline import get_identidad
from .models import (
    EvaluadorProyecto,
    Linea,
    MemoriaRespuesta,
    ParticipanteProyecto,
    Programa,
    Proyecto,
    TipoParticipacion,
)


class AsignarCorrectorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['corrector'].widget.choices = BLANK_CHOICE_DASH + [
            (u.id, u.full_name)
            for u in Group.objects.get(name='Correctores')
            .user_set.order_by('first_name', 'last_name', 'last_name_2')
            .all()
        ]

    class Meta:
        fields = ('corrector',)
        model = Proyecto


class AyudaForm(forms.Form):
    """Crea un ticket en OTRS"""

    asunto = forms.CharField(
        help_text=_(
            'Ejemplo: '
            'Asignar la vinculación «Participantes externos Proyectos Innovación Docente» a un NIP'
        ),
        label=_('Asunto'),
        max_length=255,
        required=True,
    )
    descripcion = forms.CharField(
        label=_('Descripción'),
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': _('Explique lo que desea, indicando todos los datos necesarios.')
            }
        ),
    )


class CorreccionForm(forms.ModelForm):
    BOOL_CHOICES = ((True, _('Sí')), (False, _('No')))
    aceptacion_corrector = forms.ChoiceField(
        label=_('Se admite'), widget=forms.RadioSelect, choices=BOOL_CHOICES
    )
    es_publicable = forms.ChoiceField(widget=forms.RadioSelect, choices=BOOL_CHOICES)

    class Meta:
        fields = ('aceptacion_corrector', 'es_publicable', 'observaciones_corrector')
        model = Proyecto


class HaceConstarForm(forms.Form):
    nip = forms.IntegerField(
        label=_('NIP'),
        help_text=_(
            'Número de Identificación Personal en la Universidad de Zaragoza'
            ' de la persona para la que desee generar el Hace Constar.'
        ),
        min_value=0,
        max_value=9_999_999,
        required=False,
    )
    email = forms.EmailField(
        label=_('E-mail'),
        help_text=_(
            'Dirección de correo electrónico de la persona para la que desee generar'
            ' el Hace Constar.'
        ),
        required=False,
    )


class CertificadoForm(forms.Form):
    nif = forms.CharField(
        label=_('NIF'),
        help_text=_(
            'En ausencia de NIP asociado, NIF de la persona para la que desee generar'
            ' el Certificado.'
        ),
        max_length=20,
        required=True,
    )


class CorrectorForm(forms.Form):
    nip = forms.IntegerField(
        label=_('NIP'),
        help_text=_(
            'Número de Identificación Personal en la Universidad de Zaragoza'
            ' de la persona a añadir al grupo de correctores de memorias.'
        ),
        min_value=0,
        max_value=9_999_999,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_action = 'corrector_anyadir'
        self.helper.form_class = 'form-inline'
        # self.helper.wrapper_class = 'col-7'
        # self.helper.label_class = 'margin-right-1'
        # self.helper.field_class = 'margin-right-1'
        self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        self.helper.layout = Layout(
            'nip',
            ButtonHolder(
                StrictButton(
                    f"<span class='fas fa-user-plus'></span> {_('Añadir')}",
                    css_class='btn btn-warning',
                    title=_('Añadir al titular de este NIP como corrector'),
                    type='submit',
                ),
                css_class='margin-left-1',
            ),
        )


class InvitacionForm(forms.ModelForm):
    nip = forms.IntegerField(
        label=_('NIP'),
        help_text=_(
            'Número de Identificación Personal en la Universidad de Zaragoza'
            ' de la persona a invitar.'
        ),
    )

    def __init__(self, *args, **kwargs):
        # Override __init__ to make the "self" object have the proyecto instance
        # designated by the proyecto_id sent by the view, taken from the URL parameter.
        self.proyecto = Proyecto.objects.get(id=kwargs.pop('proyecto_id'))
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def _crear_usuario(self, nip):
        '''Crea un registro de usuario con el nip indicado y los datos de G.I.'''

        usuario = CustomUser.objects.create_user(username=nip)
        try:
            get_identidad(load_strategy(self.request), None, usuario)
        except Exception as ex:
            # Si Gestión de Identidades devuelve un error, borramos el usuario
            # y finalizamos mostrando el mensaje de error.
            usuario.delete()
            raise forms.ValidationError('ERROR: ' + str(ex))

        # HACK - Indicamos que la autenticación es vía Single Sign On con SAML, y el IdP usado.
        usuario_social = UserSocialAuth(
            uid=f'sir:{usuario.username}', provider='saml', user=usuario
        )
        usuario_social.save()

        return usuario

    def clean(self):
        # See <https://docs.djangoproject.com/en/dev/ref/forms/validation/>
        # <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-modelform-clean-method>
        cleaned_data = super().clean()
        nip = cleaned_data.get('nip')
        # Comprobamos si el usuario ya existe en el sistema.
        usuario = CustomUser.objects.get_or_none(username=nip)

        # Si no existe previamente, lo creamos y actualizamos con los datos de Identidades.
        if not usuario:
            usuario = self._crear_usuario(nip)

        # El usuario existe. Actualizamos sus datos con los de Gestión de Identidades.
        try:
            get_identidad(load_strategy(self.request), None, usuario)
        except Exception as ex:
            # Si Identidades devuelve un error, finalizamos mostrando el mensaje de error.
            raise forms.ValidationError('ERROR: ' + str(ex))

        # Si el usuario no está activo, finalizamos explicando esta circunstancia.
        if not usuario.is_active:
            raise forms.ValidationError(
                mark_safe(
                    _(
                        f'''Usuario inactivo en el sistema de Gestión de Identidades.<br>
                        <a href="{ reverse('ayuda') }">Solicite en Ayudica</a> que se le asigne
                        la vinculación «Participantes externos Proyectos Innovación Docente».'''
                    )
                )
            )

        # Si el usuario no tiene un email válido, finalizamos explicando esta circunstancia.
        if not usuario.email:
            raise forms.ValidationError(
                _(
                    f'No fue posible invitar al usuario «{nip}» porque no tiene '
                    'establecida ninguna dirección de correo electrónico en el sistema '
                    'de Gestión de Identidades.'
                )
            )

        cleaned_data['usuario'] = usuario
        # Si un usuario ya está vinculado al proyecto, no se le puede invitar.
        vinculados = self.proyecto.get_usuarios_vinculados()
        if usuario in vinculados:
            raise forms.ValidationError(
                _(
                    f'No puede invitar a {usuario.full_name} '
                    'porque ya está vinculado a este proyecto.'
                )
            )
        # En algunos programas la participación de los estudiantes puede estar limitada
        # (por ejemplo a dos por proyecto)
        if self.proyecto.programa.max_estudiantes and usuario.get_colectivo_principal() == 'EST':
            estudiantes = [
                vinculado
                for vinculado in vinculados
                if vinculado.get_colectivo_principal() == 'EST'
            ]
            if len(estudiantes) >= self.proyecto.programa.max_estudiantes:
                nombres_estudiantes = ', '.join(list(map(lambda e: e.full_name, estudiantes)))
                raise forms.ValidationError(
                    _(
                        'Ya se ha alcanzado el máximo de participación de '
                        f'{self.proyecto.programa.max_estudiantes} estudiantes '
                        f'por proyecto: {nombres_estudiantes}.'
                    )
                )

        return cleaned_data

    def save(self, commit=True):
        invitado = super().save(commit=False)
        invitado.proyecto = self.proyecto
        invitado.tipo_participacion = TipoParticipacion('invitado')
        invitado.usuario = self.cleaned_data['usuario']
        return invitado.save()

    class Meta:
        fields = ['nip']
        model = ParticipanteProyecto


class ProyectoFilterFormHelper(FormHelper):
    """
    Formulario para filtrar el listado de todos los proyectos.

    Ver https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
    """

    form_class = 'form form-inline'
    form_id = 'proyecto-filter-form'
    form_method = 'GET'
    form_tag = True
    html5_required = True
    layout = Layout(
        Fieldset(
            '<span class="fas fa-filter"></span> ' + str(_('Filtrar proyectos')),
            Div(InlineField('estado', wrapper_class='col-4'), css_class='row'),
            css_class='col-10 border p-3',
        ),
        ButtonHolder(Submit('submit', _('Filtrar')), css_class='col-2 text-center'),
    )


class ProyectoForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        programa = cleaned_data.get('programa')
        linea = cleaned_data.get('linea')
        lineas_del_programa = programa.lineas.all()
        centro = cleaned_data.get('centro')
        estudio = cleaned_data.get('estudio')

        if linea and linea.programa_id != programa.id:
            self.add_error(
                'linea', _('La línea seleccionada no pertenece al programa seleccionado.')
            )

        if lineas_del_programa and not linea:
            self.add_error('linea', _('Este programa requiere seleccionar una línea.'))

        if programa.nombre_corto == 'PIET' and not estudio:
            self.add_error('estudio', _('Los PIET deben estar vinculados a un estudio.'))

        if programa.nombre_corto == 'PIPOUZ' and centro:
            if not centro.nips_coord_pou:
                self.add_error('centro', _('El centro carece de coordinador del POU.'))
            elif self.instance.user.username not in centro.nips_coord_pou:
                self.add_error(
                    'programa',
                    _(
                        'En los proyectos PIPOUZ el coordinador deberá ser '
                        'el coordinador del POU del centro.'
                    ),
                )

        # In Django < 1.7, `form.clean()` was required to return a dictionary of `cleaned_data`.
        # This method may still return a dictionary of data to be used, but it's no longer required

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['programa'].widget.choices = BLANK_CHOICE_DASH + list(
            Programa.objects.filter(convocatoria_id=date.today().year)
            .values_list('id', 'nombre_corto')
            .all()
        )
        self.fields['linea'].widget.choices = BLANK_CHOICE_DASH + list(
            Linea.objects.filter(programa__convocatoria_id=date.today().year)
            .values_list('id', 'nombre')
            .all()
        )
        centros_del_usuario = list((c.id, str(c)) for c in self.user.centros)
        self.fields['centro'].widget.choices = (
            BLANK_CHOICE_DASH + centros_del_usuario
            if len(centros_del_usuario) > 1
            else centros_del_usuario
        )
        # Las opciones de `estudio` están limitadas con `limit_choices_to` en el modelo `Proyecto`

    class Meta:
        fields = ['titulo', 'descripcion', 'programa', 'linea', 'centro', 'estudio']
        model = Proyecto


class EvaluadorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Override __init__ to make the "self" object have the proyecto instance
        # designated by the proyecto_id sent by the view, taken from the URL parameter.
        self.proyecto = Proyecto.objects.get(id=kwargs.pop('proyecto_id'))
        super().__init__(*args, **kwargs)
        # Content of the dropdown
        self.fields['evaluador'].widget.choices = BLANK_CHOICE_DASH + [
            (u.id, u.full_name)
            for u in Group.objects.get(name="Evaluadores")
            .user_set.order_by('first_name', 'last_name', 'last_name_2')
            .all()
        ]

    def save(self, commit=True):
        # evaluadorproyecto = super().save(commit=False)
        # evaluadorproyecto.proyecto = self.proyecto
        # evaluadorproyecto.evaluador = self.cleaned_data['evaluador']
        # return evaluadorproyecto.save()
        return self.proyecto.evaluadores.add(self.cleaned_data['evaluador'])

    class Meta:
        fields = ('evaluador',)
        model = EvaluadorProyecto


class MemoriaRespuestaForm(forms.ModelForm):
    texto = SummernoteTextField()

    class Meta:
        fields = ('texto',)
        model = MemoriaRespuesta
        widgets = {'texto': SummernoteWidget()}

    def as_p(self):
        """
        Return this form rendered as HTML <p>s, without label but with help for this subitem.

        Overrides `BaseForm.as_p()`.
        """

        return self._html_output(
            normal_row='<p%(html_class_attr)s> %(field)s'
            + self.instance.subapartado.ayuda
            + '</p>',
            error_row='%s',
            row_ender='</p>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )


class ResolucionForm(forms.ModelForm):
    class Meta:
        fields = (
            'aceptacion_comision',
            'ayuda_provisional',
            'ayuda_definitiva',
            'tipo_gasto',
            'puntuacion',
            'observaciones',
        )
        model = Proyecto
