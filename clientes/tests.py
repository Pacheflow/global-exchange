from django.test import TestCase
from django.urls import reverse

from .forms import ClienteForm
from .models import CategoriaCliente, Cliente


class ClienteModelTest(TestCase):

    def test_crear_categoria_cliente(self):
        categoria = CategoriaCliente.objects.create(
            nombre="Categoria Prueba",
            descripcion="Categoría utilizada para pruebas"
        )

        self.assertEqual(
            categoria.nombre,
            "Categoria Prueba"
        )

    def test_crear_cliente(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Prueba",
            tipo_persona="FISICA",
            documento="123456"
        )

        self.assertEqual(
            cliente.nombre_razon_social,
            "Cliente Prueba"
        )

    def test_estado_activo_por_defecto(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Activo",
            tipo_persona="FISICA",
            documento="111111"
        )

        self.assertEqual(
            cliente.estado,
            "ACTIVO"
        )

    def test_dar_de_baja_cliente(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Baja",
            tipo_persona="FISICA",
            documento="222222"
        )

        cliente.dar_de_baja()

        self.assertEqual(
            cliente.estado,
            "INACTIVO"
        )

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

        self.assertFalse(
            form.is_valid()
        )

    def test_documento_puede_ser_alfanumerico(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Extranjero",
            tipo_persona="FISICA",
            documento="AB123456"
        )

        self.assertEqual(
            cliente.documento,
            "AB123456"
        )

    def test_documento_puede_contener_guion(self):
        cliente = Cliente.objects.create(
            nombre_razon_social="Empresa Prueba",
            tipo_persona="JURIDICA",
            documento="80012345-6"
        )

        self.assertEqual(
            cliente.documento,
            "80012345-6"
        )

    def test_nombre_es_obligatorio(self):
        form = ClienteForm(data={
            "nombre_razon_social": "",
            "tipo_persona": "FISICA",
            "documento": "555555"
        })

        self.assertFalse(
            form.is_valid()
        )

    def test_documento_es_obligatorio(self):
        form = ClienteForm(data={
            "nombre_razon_social": "Cliente Sin Documento",
            "tipo_persona": "FISICA",
            "documento": ""
        })

        self.assertFalse(
            form.is_valid()
        )

    def test_tipo_persona_invalido(self):
        form = ClienteForm(data={
            "nombre_razon_social": "Cliente Prueba",
            "tipo_persona": "OTRO",
            "documento": "666666"
        })

        self.assertFalse(
            form.is_valid()
        )


class RegistrarClienteViewTest(TestCase):

    def test_mostrar_formulario_registro(self):
        response = self.client.get(
            reverse("registrar_cliente")
        )

        self.assertEqual(
            response.status_code,
            200
        )

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

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            Cliente.objects.filter(
                documento="444444"
            ).exists()
        )


class ConsultarClienteViewTest(TestCase):

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Consulta",
            tipo_persona="FISICA",
            documento="CONSULTA-001"
        )

    def test_consultar_clientes(self):
        response = self.client.get(
            reverse("consultar_clientes")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            "Cliente Consulta"
        )

    def test_buscar_cliente_por_nombre(self):
        response = self.client.get(
            reverse("consultar_clientes"),
            {
                "buscar": "Consulta"
            }
        )

        self.assertContains(
            response,
            "Cliente Consulta"
        )

    def test_consulta_sin_resultados(self):
        response = self.client.get(
            reverse("consultar_clientes"),
            {
                "buscar": "NoExiste"
            }
        )

        self.assertContains(
            response,
            "No se encontraron clientes."
        )


class EditarClienteViewTest(TestCase):

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Original",
            tipo_persona="FISICA",
            documento="EDITAR-001"
        )

    def test_editar_cliente(self):
        response = self.client.post(
            reverse(
                "editar_cliente",
                args=[self.cliente.id]
            ),
            {
                "nombre_razon_social": "Cliente Editado",
                "tipo_persona": "JURIDICA",
                "documento": "EDITAR-001"
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.nombre_razon_social,
            "Cliente Editado"
        )

        self.assertEqual(
            self.cliente.tipo_persona,
            "JURIDICA"
        )

    def test_no_permite_documento_duplicado_al_editar(self):
        Cliente.objects.create(
            nombre_razon_social="Otro Cliente",
            tipo_persona="FISICA",
            documento="DOCUMENTO-OTRO"
        )

        response = self.client.post(
            reverse(
                "editar_cliente",
                args=[self.cliente.id]
            ),
            {
                "nombre_razon_social": "Cliente Modificado",
                "tipo_persona": "FISICA",
                "documento": "DOCUMENTO-OTRO"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.documento,
            "EDITAR-001"
        )


class DarDeBajaClienteViewTest(TestCase):

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Baja Vista",
            tipo_persona="FISICA",
            documento="BAJA-001"
        )

    def test_dar_de_baja_cliente(self):
        response = self.client.post(
            reverse(
                "dar_de_baja_cliente",
                args=[self.cliente.id]
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.estado,
            "INACTIVO"
        )

        self.assertTrue(
            Cliente.objects.filter(
                id=self.cliente.id
            ).exists()
        )


class SegmentarClienteViewTest(TestCase):

    def setUp(self):
        self.categoria, _ = CategoriaCliente.objects.get_or_create(
            nombre="VIP",
            defaults={
                "descripcion": "Cliente VIP"
            }
        )

        self.cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Segmentado",
            tipo_persona="FISICA",
            documento="SEGMENTAR-001"
        )

    def test_segmentar_cliente(self):
        response = self.client.post(
            reverse(
                "segmentar_cliente",
                args=[self.cliente.id]
            ),
            {
                "categoria": self.categoria.id
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.categoria,
            self.categoria
        )

    def test_cambiar_categoria_cliente(self):
        otra_categoria = CategoriaCliente.objects.create(
            nombre="Corporativo Prueba"
        )

        self.cliente.categoria = self.categoria
        self.cliente.save()

        self.client.post(
            reverse(
                "segmentar_cliente",
                args=[self.cliente.id]
            ),
            {
                "categoria": otra_categoria.id
            }
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.categoria,
            otra_categoria
        )


class SeleccionarClienteViewTest(TestCase):

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre_razon_social="Cliente Operativo",
            tipo_persona="JURIDICA",
            documento="OPERAR-001",
        )

    def test_seleccionar_cliente_activo_guarda_contexto_en_sesion(self):
        response = self.client.post(
            reverse("seleccionar_cliente", args=[self.cliente.id])
        )

        self.assertRedirects(
            response,
            reverse("usuarios:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            self.client.session["selected_client"],
            {"id": self.cliente.id, "name": "Cliente Operativo"},
        )

    def test_cliente_inactivo_no_puede_seleccionarse(self):
        self.cliente.dar_de_baja()

        response = self.client.post(
            reverse("seleccionar_cliente", args=[self.cliente.id])
        )

        self.assertEqual(response.status_code, 404)
