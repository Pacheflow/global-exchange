from django import forms
from .models import Cliente


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