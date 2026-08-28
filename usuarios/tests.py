from django.test import TestCase
from django.urls import reverse


class RegistroUsuarioTests(TestCase):
    def test_ruta_registro_existe(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertEqual(response.status_code, 302)

    def test_registro_redirige_a_keycloak(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "http://localhost:8080/realms/global-exchange/"
            "protocol/openid-connect/registrations",
            response.url,
        )

    def test_registro_usa_cliente_correcto(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "client_id=global-exchange-web",
            response.url,
        )
