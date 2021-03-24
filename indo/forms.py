# Standard library
from datetime import date

# Third-party
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

# Django
from django import forms
from django.contrib.auth.models import Group
from django.db.models import BLANK_CHOICE_DASH
from django.utils.translation import gettext_lazy as _

# Local Django
from accounts.models import CustomUser
from accounts.pipeline import get_identidad
from .models import (
    Linea,
    MemoriaRespuesta,
    ParticipanteProyecto,
    Programa,
    Proyecto,
    TipoParticipacion,
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

        # HACK - Indicamos que la autenticación es vía Single Sign On con SAML.
        usuario_social = UserSocialAuth(
            uid=f'lord:{usuario.username}', provider='saml', user=usuario
        )
        usuario_social.save()

        return usuario

    def clean(self):
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
                _('Usuario inactivo en el sistema de Gestión de Identidades')
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
                    f'No puede invitar a {usuario.get_full_name()} '
                    'porque ya está vinculado a este proyecto.'
                )
            )
        # La participación de los estudiantes estará limitada a dos por proyecto
        # (excepto en los PIPOUZ).
        if (
            self.proyecto.programa.nombre_corto != 'PIPOUZ'
            and usuario.get_colectivo_principal() == 'EST'
        ):
            estudiantes = [
                vinculado
                for vinculado in vinculados
                if vinculado.get_colectivo_principal() == 'EST'
            ]
            if len(estudiantes) >= self.proyecto.programa.max_estudiantes:
                nombres_estudiantes = ', '.join(
                    list(map(lambda e: e.get_full_name(), estudiantes))
                )
                raise forms.ValidationError(
                    _(
                        'Ya se ha alcanzado el máximo de participación de '
                        f'{self.proyecto.programa.max_estudiantes} estudiantes '
                        f'por proyecto: {nombres_estudiantes}.'
                    )
                )

    def save(self, commit=True):
        invitado = super().save(commit=False)
        invitado.proyecto = self.proyecto
        invitado.tipo_participacion = TipoParticipacion('invitado')
        invitado.usuario = self.cleaned_data['usuario']
        return invitado.save()

    class Meta:
        fields = ['nip']
        model = ParticipanteProyecto


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

        if programa.nombre_corto in ('PIEC', 'PRACUZ', 'PIPOUZ') and not centro:
            self.add_error('centro', _('Este programa debe estar vinculado a un centro.'))

        if programa.nombre_corto == 'PIET' and not estudio:
            self.add_error('estudio', _('Los PIET deben estar vinculados a un estudio.'))

        if programa.nombre_corto == 'PIPOUZ':
            if not hasattr(centro, 'nips_coord_pou'):
                self.add_error('centro', _('El centro carece de coordinador del POU.'))
            elif self.instance.user.username not in centro.nips_coord_pou:
                self.add_error(
                    'programa',
                    _(
                        'En los proyectos PIPOUZ el coordinador deberá ser '
                        'el coordinador del POU del centro.'
                    ),
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['programa'].widget.choices = tuple(
            BLANK_CHOICE_DASH
            + list(
                Programa.objects.filter(convocatoria_id=date.today().year)
                .values_list('id', 'nombre_corto')
                .all()
            )
        )
        self.fields['linea'].widget.choices = tuple(
            BLANK_CHOICE_DASH
            + list(
                Linea.objects.filter(programa__convocatoria_id=date.today().year)
                .values_list('id', 'nombre')
                .all()
            )
        )

    class Meta:
        fields = ['titulo', 'descripcion', 'programa', 'linea', 'centro', 'estudio']
        model = Proyecto


class EvaluadorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evaluador'].widget.choices = tuple(
            BLANK_CHOICE_DASH
            + [
                (u.id, u.full_name)
                for u in Group.objects.get(name="Evaluadores")
                .user_set.order_by('first_name', 'last_name', 'last_name_2')
                .all()
            ]
        )

    class Meta:
        fields = ('evaluador',)
        model = Proyecto


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
        fields = ('aceptacion_comision', 'ayuda_concedida', 'tipo_gasto', 'observaciones')
        model = Proyecto
