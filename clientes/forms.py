from django import forms
from .models import Cliente, UsuarioCliente


class ClienteForm(forms.ModelForm):
    """Formulario utilizado para registrar clientes en Global Exchange."""

    class Meta:
        model = Cliente

        fields = [
            "nombre_razon_social",
            "tipo_persona",
            "documento",
        ]

        labels = {
            "nombre_razon_social": "Nombre o razón social",
            "tipo_persona": "Tipo de persona",
            "documento": "Documento",
        }


class SegmentacionClienteForm(forms.ModelForm):
    """Formulario utilizado para asignar una categoría a un cliente."""

    class Meta:
        model = Cliente

        fields = [
            "categoria",
        ]

        labels = {
            "categoria": "Categoría del cliente",
        }


class AsignacionUsuarioClienteForm(forms.Form):
    usuario = forms.ChoiceField(label="Usuario de Keycloak")
    rol_en_cliente = forms.ChoiceField(
        label="Permiso dentro del cliente",
        choices=UsuarioCliente.ROLES,
    )

    def __init__(self, *args, usuarios=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario"].choices = [
            (user["id"], user["label"]) for user in usuarios
        ]
