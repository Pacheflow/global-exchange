from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from jwt.exceptions import (
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidTokenError,
)

from .services.keycloak import (
    SESSION_AUTENTICADO,
    SESSION_ROLES,
    SESSION_USUARIO,
    extraer_roles_sistema,
    validar_access_token,
)

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
    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_callback_login_exitoso(self, mock_post, mock_validar_token):

        session = self.client.session
        session["code_verifier"] = "verificador-prueba"
        session.save()

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}
        mock_validar_token.return_value = {
            "sub": "usuario-keycloak-1",
            "preferred_username": "admin.prueba",
            "email": "admin@example.com",
            "realm_access": {
                "roles": ["ADMINISTRADOR", "offline_access"],
            },
        }

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
            response.json()["roles"],
            ["ADMINISTRADOR"],
        )

        self.assertNotIn("access_token", response.json())

        session = self.client.session
        self.assertTrue(session[SESSION_AUTENTICADO])
        self.assertEqual(
            session[SESSION_USUARIO]["sub"],
            "usuario-keycloak-1",
        )

    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_callback_rechaza_token_invalido(
        self,
        mock_post,
        mock_validar_token,
    ):
        session = self.client.session
        session["code_verifier"] = "verificador-prueba"
        session.save()

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-invalido"}
        mock_validar_token.side_effect = InvalidTokenError("Token inválido")

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(SESSION_AUTENTICADO, self.client.session)


class PerfilUsuarioTests(TestCase):
    """
    Verifica que el sistema devuelva correctamente
    los roles asociados al usuario autenticado.
    Corresponde a la HU-04: Gestionar accesos.
    """

    def test_perfil_devuelve_roles_usuario(self):
        session = self.client.session
        session[SESSION_AUTENTICADO] = True
        session[SESSION_USUARIO] = {
            "sub": "usuario-keycloak-1",
            "username": "admin.prueba",
            "email": "admin@example.com",
        }
        session[SESSION_ROLES] = ["ADMINISTRADOR"]
        session.save()

        response = self.client.get(reverse("usuarios:perfil_usuario"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["roles"], ["ADMINISTRADOR"])

    def test_perfil_rechaza_usuario_no_autenticado(self):
        response = self.client.get(reverse("usuarios:perfil_usuario"))

        self.assertEqual(response.status_code, 401)


class AutorizacionBackendTests(TestCase):

    def autenticar_con_roles(self, roles):
        session = self.client.session
        session[SESSION_AUTENTICADO] = True
        session[SESSION_USUARIO] = {
            "sub": "usuario-keycloak-1",
            "username": "usuario.prueba",
            "email": "usuario@example.com",
        }
        session[SESSION_ROLES] = roles
        session.save()

    def test_administrador_accede_a_vista_protegida(self):
        self.autenticar_con_roles(["ADMINISTRADOR"])

        response = self.client.get(reverse("usuarios:acceso_administrador"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Acceso administrativo permitido",
        )

    def test_usuario_sin_rol_recibe_403(self):
        self.autenticar_con_roles(["USUARIO"])

        response = self.client.get(reverse("usuarios:acceso_administrador"))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Acceso denegado")

    def test_usuario_no_autenticado_recibe_401(self):
        response = self.client.get(reverse("usuarios:acceso_administrador"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "Autenticación requerida")


class RolesKeycloakTests(TestCase):

    def test_extrae_solo_roles_definidos_por_el_sistema(self):
        claims = {
            "realm_access": {
                "roles": [
                    "ADMINISTRADOR",
                    "USUARIO",
                    "offline_access",
                    "uma_authorization",
                ],
            },
        }

        self.assertEqual(
            extraer_roles_sistema(claims),
            ["ADMINISTRADOR", "USUARIO"],
        )

    @patch(
        "usuarios.services.keycloak.jwt.get_unverified_header",
        return_value={"alg": "none"},
    )
    def test_rechaza_token_sin_algoritmo_de_firma(self, _mock_header):
        with self.assertRaises(InvalidAlgorithmError):
            validar_access_token("token-sin-firma")

    @patch("usuarios.services.keycloak.jwt.decode")
    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    @patch(
        "usuarios.services.keycloak.jwt.get_unverified_header",
        return_value={"alg": "RS256"},
    )
    def test_validacion_exige_firma_issuer_y_cliente(
        self,
        _mock_header,
        mock_cliente_jwks,
        mock_decode,
    ):
        mock_cliente_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            "clave-publica"
        )
        mock_decode.return_value = {
            "sub": "usuario-keycloak-1",
            "iss": "http://localhost:8080/realms/global-exchange",
            "iat": 1,
            "exp": 2,
            "azp": "global-exchange-web",
        }

        claims = validar_access_token("token-firmado")

        self.assertEqual(claims["sub"], "usuario-keycloak-1")
        opciones = mock_decode.call_args.kwargs["options"]
        self.assertTrue(opciones["verify_signature"])
        self.assertTrue(opciones["verify_exp"])
        self.assertTrue(opciones["verify_iss"])
        self.assertEqual(
            mock_decode.call_args.kwargs["issuer"],
            f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}"
            f"/realms/{settings.KEYCLOAK_REALM}",
        )
        self.assertEqual(
            mock_decode.call_args.kwargs["algorithms"],
            ["RS256"],
        )
        mock_cliente_jwks.assert_called_once_with(
            f"{settings.KEYCLOAK_INTERNAL_URL.rstrip('/')}"
            f"/realms/{settings.KEYCLOAK_REALM}"
            "/protocol/openid-connect/certs"
        )

    @patch("usuarios.services.keycloak.jwt.decode")
    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    @patch(
        "usuarios.services.keycloak.jwt.get_unverified_header",
        return_value={"alg": "RS256"},
    )
    def test_rechaza_token_emitido_para_otro_cliente(
        self,
        _mock_header,
        mock_cliente_jwks,
        mock_decode,
    ):
        mock_cliente_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            "clave-publica"
        )
        mock_decode.return_value = {
            "sub": "usuario-keycloak-1",
            "iss": "http://localhost:8080/realms/global-exchange",
            "iat": 1,
            "exp": 2,
            "azp": "otro-cliente",
            "aud": ["account"],
        }

        with self.assertRaises(InvalidAudienceError):
            validar_access_token("token-de-otro-cliente")
