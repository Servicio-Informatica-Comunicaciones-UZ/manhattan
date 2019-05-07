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

    def __init__(self, *args, **kwargs):
        # Override __init__ to make the "self" object have the proyecto instance
        # designated by the proyecto_id sent by the view, taken from the URL parameter.
        self.proyecto = Proyecto.objects.get(id=kwargs.pop("proyecto_id"))
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nip = cleaned_data.get("nip")
        cleaned_data["usuario"] = CustomUser.objects.get(username=nip)
        # TODO Si el usuario no existe, crearlo.

    def save(self, commit=True):
        invitado = super().save(commit=False)
        invitado.proyecto = self.proyecto
        invitado.tipo_participacion = TipoParticipacion("invitado")
        invitado.usuario = self.cleaned_data["usuario"]
        return invitado.save()

    class Meta:
        fields = ["nip"]
        model = ParticipanteProyecto


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
