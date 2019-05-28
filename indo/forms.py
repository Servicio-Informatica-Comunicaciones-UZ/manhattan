from django import forms
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy
from .models import ParticipanteProyecto, Proyecto, TipoParticipacion
from accounts.models import CustomUser as CustomUser
from accounts.pipeline import get_identidad, UsuarioNoEncontrado


class InvitacionForm(forms.ModelForm):
    nip = forms.IntegerField(
        label=_("NIP"),
        help_text=_(
            "Número de Identificación Personal en la Universidad de Zaragoza "
            "de la persona a invitar."
        ),
    )

    def __init__(self, *args, **kwargs):
        # Override __init__ to make the "self" object have the proyecto instance
        # designated by the proyecto_id sent by the view, taken from the URL parameter.
        self.proyecto = Proyecto.objects.get(id=kwargs.pop("proyecto_id"))
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nip = cleaned_data.get("nip")
        usuario = CustomUser.objects.get_or_none(username=nip)
        if not usuario:
            usuario = CustomUser.objects.create_user(username=nip)
            try:
                get_identidad(load_strategy(self.request), None, usuario)
            except UsuarioNoEncontrado:
                usuario.delete()
                raise forms.ValidationError(
                    _(f"¡Usuario desconocido! No se ha encontrado el NIP «{nip}».")
                )
            # HACK
            usuario_social = UserSocialAuth(
                uid=f"lord:{usuario.username}", provider="saml", user=usuario
            )
            usuario_social.save()

        get_identidad(load_strategy(self.request), None, usuario)
        if not usuario.is_active:
            raise forms.ValidationError(
                _("Usuario inactivo en el sistema de Gestión de Identidades")
            )
        if not usuario.email:
            raise forms.ValidationError(
                _(
                    f"No fue posible invitar al usuario «{nip}» porque no tiene "
                    "establecida ninguna dirección de correo electrónico en el sistema "
                    "de Gestión de Identidades."
                )
            )

        cleaned_data["usuario"] = usuario
        # La participación de los estudiantes estará limitada a dos por proyecto
        # (excepto en los PIPOUZ).
        if (
            self.proyecto.programa.nombre_corto != "PIPOUZ"
            and usuario.get_colectivo_principal() == "EST"
        ):
            vinculados = self.proyecto.get_usuarios_vinculados()
            estudiantes = []
            for vinculado in vinculados:
                if vinculado.get_colectivo_principal() == "EST":
                    estudiantes.append(vinculado)
            if len(estudiantes) >= self.proyecto.programa.max_estudiantes:
                nombres_estudiantes = ", ".join(
                    list(map(lambda e: e.get_full_name(), estudiantes))
                )
                raise forms.ValidationError(
                    _(
                        "Ya se ha alcanzado el máximo de participación de "
                        f"{self.proyecto.programa.max_estudiantes} estudiantes "
                        f"por proyecto: {nombres_estudiantes}."
                    )
                )

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
        centro = cleaned_data.get("centro")
        estudio = cleaned_data.get("estudio")

        if linea and linea.programa_id != programa.id:
            self.add_error(
                "linea",
                _("La línea seleccionada no pertenece al programa seleccionado."),
            )

        if lineas_del_programa and not linea:
            self.add_error("linea", _("Este programa requiere seleccionar una línea."))

        if programa.nombre_corto in ("PIEC", "PRACUZ", "PIPOUZ") and not centro:
            self.add_error(
                "centro", _("Este programa debe estar vinculado a un centro.")
            )

        if programa.nombre_corto == "PIET" and not estudio:
            self.add_error("estudio", _("Los PIET deben estar vinculado a un estudio."))

    class Meta:
        fields = ["titulo", "descripcion", "programa", "linea", "centro", "estudio"]
        model = Proyecto
