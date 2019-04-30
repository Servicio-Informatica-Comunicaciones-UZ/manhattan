from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Linea, Programa, Proyecto


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

        return cleaned_data

    class Meta:
        fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]
        model = Proyecto
