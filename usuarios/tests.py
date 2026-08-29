from django.test import TestCase
from django.urls import reverse


class RegistroUsuarioTests(TestCase):

    # Verifica que la ruta de registro exista
    # y que Django redirija correctamente hacia Keycloak.
    def test_ruta_registro_existe(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertEqual(response.status_code, 302)

    # Verifica que el usuario sea enviado al endpoint
    # de registro configurado en Keycloak.
    def test_registro_redirige_a_keycloak(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "http://localhost:8080/realms/global-exchange/"
            "protocol/openid-connect/registrations",
            response.url,
        )

    # Verifica que Django utilice el cliente correcto
    # configurado en Keycloak.
    def test_registro_usa_cliente_correcto(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "client_id=global-exchange-web",
            response.url,
        )

    # Verifica que la aplicación utilice el Realm correcto.
    def test_registro_usa_realm_correcto(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "/realms/global-exchange/",
            response.url,
        )

    # Verifica que el flujo utilizado sea Authorization Code Flow.
    def test_registro_usa_authorization_code_flow(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "response_type=code",
            response.url,
        )

    # Verifica que la solicitud incluya OpenID Connect.
    def test_registro_solicita_scope_openid(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertIn(
            "scope=openid",
            response.url,
        )

    # Verifica que el proceso de registro
    # no genere errores internos del servidor.
    def test_registro_no_generar_error_servidor(self):
        response = self.client.get(reverse("usuarios:registro"))

        self.assertNotEqual(
            response.status_code,
            500,
        )
