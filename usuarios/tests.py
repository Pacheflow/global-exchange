from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

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


class LoginUsuarioTests(TestCase):

    # Verifica que la ruta de login exista
    # y redirija hacia Keycloak.
    def test_login_redirige_a_keycloak(self):
        response = self.client.get(reverse("usuarios:login"))

        self.assertEqual(response.status_code, 302)

        self.assertIn(
            "/protocol/openid-connect/auth",
            response.url,
        )

    # Verifica que el login utilice el cliente correcto.
    def test_login_usa_cliente_correcto(self):
        response = self.client.get(reverse("usuarios:login"))

        self.assertIn(
            "client_id=global-exchange-web",
            response.url,
        )

    # Verifica que el callback falle si Keycloak
    # no devuelve un código de autorización.
    def test_callback_sin_codigo(self):
        response = self.client.get(reverse("usuarios:callback"))

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json()["error"],
            "No se recibió código de autorización",
        )

    # Verifica que Django pueda intercambiar el código
    # recibido por un token de acceso.
    @patch("usuarios.views.requests.post")
    def test_callback_login_exitoso(self, mock_post):

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba"},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json()["message"],
            "Login exitoso",
        )

        self.assertEqual(
            response.json()["access_token"],
            "token-prueba",
        )


class PerfilUsuarioTests(TestCase):
    """
    Verifica que el sistema devuelva correctamente
    los roles asociados al usuario autenticado.
    Corresponde a la HU-04: Gestionar accesos.
    """

    def test_perfil_devuelve_roles_usuario(self):
        session = self.client.session
        session["roles"] = ["ADMINISTRADOR"]
        session.save()

        response = self.client.get(reverse("usuarios:perfil_usuario"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["roles"], ["ADMINISTRADOR"])
