from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Linea, Programa, ParticipanteProyecto, Proyecto, TipoParticipacion
from accounts.models import CustomUser as CustomUser


class InvitacionForm(forms.ModelForm):
    usuario_id = forms.IntegerField(help_text="NIP de la persona a invitar")

    def __init__(self, *args, **kwargs):
        # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole.
        current_user = kwargs.pop("current_user")
        proyecto_id = kwargs.pop("proyecto_id")
        super().__init__(*args, **kwargs)
        proyecto = Proyecto.objects.get(id=proyecto_id)
        self.fields["proyecto"].initial = proyecto
        tipo_participacion = TipoParticipacion.objects.get(nombre="invitado")
        self.fields["tipo_participacion"].initial = tipo_participacion
        # Se pone porque es un campo requerido, pero se sobrescribirá en clean().
        self.fields["usuario"].initial = current_user

    def clean(self):
        cleaned_data = super().clean()

        usuario_id = cleaned_data.get("usuario_id")
        cleaned_data["usuario"] = CustomUser.objects.get(username=usuario_id)
        # TODO Si el usuario no existe, crearlo

    class Meta:
        fields = ["proyecto", "tipo_participacion", "usuario", "usuario_id"]
        model = ParticipanteProyecto
        widgets = {
            "proyecto": forms.HiddenInput,
            "tipo_participacion": forms.HiddenInput,
            "usuario": forms.HiddenInput,
        }


class ProyectoForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        programa = cleaned_data.get("programa")
        linea = cleaned_data.get("linea")
        lineas_del_programa = programa.lineas.all()

        if linea and linea.programa_id != programa.id:
            self.add_error(
                "linea",
                _("La línea seleccionada no pertenece al programa seleccionado."),
            )

        if lineas_del_programa and not linea:
            self.add_error("linea", _("Este programa requiere seleccionar una línea."))

    class Meta:
        fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]
        model = Proyecto
