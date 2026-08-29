from django.test import TestCase
from django.urls import reverse

from .forms import ClienteForm
from .models import CategoriaCliente, Cliente


class ClienteModelTest(TestCase):

    def test_crear_categoria_cliente(self):
        categoria = CategoriaCliente.objects.create(
            nombre="Minorista",
            descripcion="Cliente minorista"
        )

        self.assertEqual(categoria.nombre, "Minorista")

    def test_crear_cliente(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Prueba",
            tipo_persona="FISICA",
            documento="123456"
        )

        self.assertEqual(cliente.nombre_razon_social, "Cliente Prueba")

    def test_estado_activo_por_defecto(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Activo",
            tipo_persona="FISICA",
            documento="111111"
        )

        self.assertEqual(cliente.estado, "ACTIVO")

    def test_dar_de_baja_cliente(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Baja",
            tipo_persona="FISICA",
            documento="222222"
        )

        cliente.dar_de_baja()

        self.assertEqual(cliente.estado, "INACTIVO")

    def test_documento_no_se_puede_repetir(self):
        Cliente.objects.create(
            nombre_razon_social="Primer Cliente",
            tipo_persona="FISICA",
            documento="333333"
        )

        form = ClienteForm(data={
            "nombre_razon_social": "Segundo Cliente",
            "tipo_persona": "FISICA",
            "documento": "333333"
        })

        self.assertFalse(form.is_valid())


class RegistrarClienteViewTest(TestCase):

    def test_mostrar_formulario_registro(self):
        response = self.client.get(
            reverse("registrar_cliente")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "clientes/registrar.html"
        )

    def test_registrar_cliente(self):
        response = self.client.post(
            reverse("registrar_cliente"),
            {
                "nombre_razon_social": "Cliente Nuevo",
                "tipo_persona": "FISICA",
                "documento": "444444"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Cliente.objects.filter(
                documento="444444"
            ).exists()
        )