from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Linea, Programa, ParticipanteProyecto, Proyecto, TipoParticipacion
from accounts.models import CustomUser as CustomUser


class InvitacionForm(forms.ModelForm):
    nip = forms.IntegerField(
        label=_("NIP"),
        help_text=_(
            "Número de Identificación Personal en la Universidad de Zaragoza de la persona a invitar"
        ),
    )
    # El usuario se rellenará en clean() a partir del NIP.
    usuario = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        proyecto_id = kwargs.pop("proyecto_id")
        super().__init__(*args, **kwargs)
        proyecto = Proyecto.objects.get(id=proyecto_id)
        self.fields["proyecto"].initial = proyecto

    def clean(self):
        cleaned_data = super().clean()
        nip = cleaned_data.get("nip")
        cleaned_data["usuario"] = CustomUser.objects.get(username=nip)
        # TODO Si el usuario no existe, crearlo.

    def save(self, commit=True):
        invitado = super().save(commit=False)
        invitado.tipo_participacion = TipoParticipacion("invitado")
        return invitado.save()

    class Meta:
        fields = ["proyecto", "usuario", "nip"]
        model = ParticipanteProyecto
        widgets = {"proyecto": forms.HiddenInput}


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
