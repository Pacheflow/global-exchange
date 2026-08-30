import base64
import hashlib
import json
import time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
)

from .services.keycloak import (
    SESSION_AUTENTICADO,
    SESSION_EXPIRA_EN,
    SESSION_ROLES,
    SESSION_USUARIO,
    extraer_roles_sistema,
    validar_access_token,
)
from .views import FLUJO_LOGIN, FLUJO_REGISTRO, OIDC_FLOWS_SESSION_KEY


class FlujoOIDCMixin:
    def iniciar_flujo(self, nombre_url):
        response = self.client.get(reverse(nombre_url))
        params = parse_qs(urlsplit(response.url).query)
        state = params["state"][0]
        flow = self.client.session[OIDC_FLOWS_SESSION_KEY][state]
        return response, params, state, flow

    @staticmethod
    def claims_validos(roles=None):
        return {
            "sub": "usuario-keycloak-1",
            "preferred_username": "usuario.prueba",
            "email": "usuario@example.com",
            "email_verified": True,
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "iss": settings.KEYCLOAK_EXPECTED_ISSUER,
            "azp": settings.KEYCLOAK_CLIENT_ID,
            "realm_access": {"roles": roles or ["USUARIO"]},
        }


class RegistroUsuarioTests(FlujoOIDCMixin, TestCase):
    def test_registro_redirige_a_keycloak(self):
        response, params, _, _ = self.iniciar_flujo("usuarios:registro")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlsplit(response.url).netloc, "localhost:8080")
        self.assertIn(
            "/realms/global-exchange/protocol/openid-connect/registrations",
            response.url,
        )
        self.assertEqual(params["client_id"], [settings.KEYCLOAK_CLIENT_ID])
        self.assertEqual(params["response_type"], ["code"])
        self.assertIn("openid", params["scope"][0])

    def test_registro_usa_callback_backend_configurado(self):
        _, params, _, _ = self.iniciar_flujo("usuarios:registro")

        self.assertEqual(params["redirect_uri"], [settings.OIDC_CALLBACK_URL])
        self.assertNotEqual(params["redirect_uri"], ["http://localhost:8000/"])

    def test_registro_genera_state_y_lo_asocia_al_flujo(self):
        _, params, state, flow = self.iniciar_flujo("usuarios:registro")

        self.assertEqual(params["state"], [state])
        self.assertEqual(flow["tipo_flujo"], FLUJO_REGISTRO)
        self.assertGreaterEqual(len(state), 32)

    def test_registro_usa_pkce_s256_asociado_al_state(self):
        _, params, _, flow = self.iniciar_flujo("usuarios:registro")
        verifier = flow["code_verifier"]
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )

        self.assertGreaterEqual(len(verifier), 43)
        self.assertEqual(params["code_challenge"], [challenge])
        self.assertEqual(params["code_challenge_method"], ["S256"])

    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_callback_identifica_registro(self, mock_post, mock_validar_token):
        _, _, state, _ = self.iniciar_flujo("usuarios:registro")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}
        mock_validar_token.return_value = self.claims_validos()

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": state},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["flujo"], FLUJO_REGISTRO)
        self.assertEqual(response.json()["message"], "Registro y autenticación exitosos")
        self.assertNotIn("access_token", response.json())


class LoginUsuarioTests(FlujoOIDCMixin, TestCase):
    def test_login_genera_state_y_pkce(self):
        response, params, state, flow = self.iniciar_flujo("usuarios:login")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/protocol/openid-connect/auth", response.url)
        self.assertEqual(params["state"], [state])
        self.assertEqual(params["code_challenge_method"], ["S256"])
        self.assertEqual(flow["tipo_flujo"], FLUJO_LOGIN)
        self.assertIn("code_verifier", flow)

    def test_intentos_simultaneos_conservan_verifiers_independientes(self):
        _, _, state_1, flow_1 = self.iniciar_flujo("usuarios:login")
        _, _, state_2, flow_2 = self.iniciar_flujo("usuarios:login")

        self.assertNotEqual(state_1, state_2)
        self.assertNotEqual(flow_1["code_verifier"], flow_2["code_verifier"])
        self.assertEqual(len(self.client.session[OIDC_FLOWS_SESSION_KEY]), 2)

    def test_callback_rechaza_state_faltante(self):
        self.iniciar_flujo("usuarios:login")

        response = self.client.get(
            reverse("usuarios:callback"), {"code": "codigo-prueba"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "State OIDC inválido o expirado")
        self.assertNotIn(OIDC_FLOWS_SESSION_KEY, self.client.session)

    def test_callback_rechaza_state_incorrecto(self):
        self.iniciar_flujo("usuarios:login")

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": "state-ajeno"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(OIDC_FLOWS_SESSION_KEY, self.client.session)

    def test_callback_rechaza_codigo_faltante_y_consume_state(self):
        _, _, state, _ = self.iniciar_flujo("usuarios:login")

        response = self.client.get(reverse("usuarios:callback"), {"state": state})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "No se recibió código de autorización"
        )
        self.assertNotIn(OIDC_FLOWS_SESSION_KEY, self.client.session)

    def test_callback_rechaza_state_expirado(self):
        _, _, state, _ = self.iniciar_flujo("usuarios:login")
        session = self.client.session
        session[OIDC_FLOWS_SESSION_KEY][state]["creado_en"] = (
            int(time.time()) - settings.OIDC_FLOW_MAX_AGE_SECONDS - 1
        )
        session.save()

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": state},
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(OIDC_FLOWS_SESSION_KEY, self.client.session)

    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_state_correcto_usa_su_verifier_y_crea_sesion(
        self, mock_post, mock_validar_token
    ):
        _, _, state, flow = self.iniciar_flujo("usuarios:login")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}
        mock_validar_token.return_value = self.claims_validos(["USUARIO"])

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": state},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login exitoso")
        self.assertEqual(response.json()["roles"], ["USUARIO"])
        self.assertNotIn("access_token", response.json())
        self.assertEqual(
            mock_post.call_args.kwargs["data"]["code_verifier"],
            flow["code_verifier"],
        )
        self.assertEqual(
            mock_post.call_args.kwargs["data"]["redirect_uri"],
            settings.OIDC_CALLBACK_URL,
        )
        session = self.client.session
        self.assertTrue(session[SESSION_AUTENTICADO])
        self.assertGreater(session[SESSION_EXPIRA_EN], time.time())

    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_state_ya_utilizado_es_rechazado(self, mock_post, mock_validar_token):
        _, _, state, _ = self.iniciar_flujo("usuarios:login")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}
        mock_validar_token.return_value = self.claims_validos()
        params = {"code": "codigo-prueba", "state": state}

        primera = self.client.get(reverse("usuarios:callback"), params)
        segunda = self.client.get(reverse("usuarios:callback"), params)

        self.assertEqual(primera.status_code, 200)
        self.assertEqual(segunda.status_code, 400)
        self.assertTrue(self.client.session[SESSION_AUTENTICADO])

    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_callback_rechaza_token_invalido(self, mock_post, mock_validar_token):
        _, _, state, _ = self.iniciar_flujo("usuarios:login")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "invalido"}
        mock_validar_token.side_effect = InvalidTokenError("Token inválido")

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": state},
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn(SESSION_AUTENTICADO, self.client.session)

    @override_settings(OIDC_LOGIN_SUCCESS_URL="http://localhost:3000/inicio")
    @patch("usuarios.views.validar_access_token")
    @patch("usuarios.views.requests.post")
    def test_callback_solo_usa_destino_fijo_de_frontend(
        self, mock_post, mock_validar_token
    ):
        _, _, state, _ = self.iniciar_flujo("usuarios:login")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token-prueba"}
        mock_validar_token.return_value = self.claims_validos()

        response = self.client.get(
            reverse("usuarios:callback"),
            {"code": "codigo-prueba", "state": state, "next": "https://malicioso"},
        )

        self.assertRedirects(
            response,
            "http://localhost:3000/inicio",
            fetch_redirect_response=False,
        )


class AutorizacionBackendTests(TestCase):
    def autenticar_con_roles(self, roles, expira_en=None):
        session = self.client.session
        session[SESSION_AUTENTICADO] = True
        session[SESSION_USUARIO] = {
            "sub": "usuario-keycloak-1",
            "username": "usuario.prueba",
            "email": "usuario@example.com",
        }
        session[SESSION_ROLES] = roles
        session[SESSION_EXPIRA_EN] = expira_en or int(time.time()) + 300
        session.save()

    def test_perfil_con_sesion_vigente_devuelve_identidad_y_roles(self):
        self.autenticar_con_roles(["USUARIO"])

        response = self.client.get(reverse("usuarios:perfil_usuario"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["roles"], ["USUARIO"])

    def test_perfil_rechaza_sesion_expirada_y_limpia_autenticacion(self):
        self.autenticar_con_roles(["ADMINISTRADOR"], int(time.time()) - 1)

        response = self.client.get(reverse("usuarios:perfil_usuario"))

        self.assertEqual(response.status_code, 401)
        self.assertNotIn(SESSION_AUTENTICADO, self.client.session)
        self.assertNotIn(SESSION_ROLES, self.client.session)

    def test_administrador_vigente_accede_a_vista_protegida(self):
        self.autenticar_con_roles(["ADMINISTRADOR"])

        response = self.client.get(reverse("usuarios:acceso_administrador"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Acceso administrativo permitido")

    def test_usuario_sin_rol_administrador_recibe_403(self):
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
                    "rol-inventado",
                ]
            }
        }

        self.assertEqual(
            extraer_roles_sistema(claims), ["ADMINISTRADOR", "USUARIO"]
        )

    def test_rol_usuario_es_aceptado(self):
        claims = {"realm_access": {"roles": ["USUARIO"]}}

        self.assertEqual(extraer_roles_sistema(claims), ["USUARIO"])


class ValidacionTokenTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_key = cls.private_key.public_key()

    def crear_token(self, **overrides):
        claims = {
            "sub": "usuario-keycloak-1",
            "iss": settings.KEYCLOAK_EXPECTED_ISSUER,
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "azp": settings.KEYCLOAK_CLIENT_ID,
            "email_verified": True,
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    @patch(
        "usuarios.services.keycloak.jwt.get_unverified_header",
        return_value={"alg": "none"},
    )
    def test_rechaza_alg_none(self, _mock_header):
        with self.assertRaises(InvalidAlgorithmError):
            validar_access_token("token-sin-firma")

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_valida_token_rs256_con_firma_issuer_expiracion_y_cliente(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )

        claims = validar_access_token(self.crear_token())

        self.assertEqual(claims["sub"], "usuario-keycloak-1")
        mock_jwks.assert_called_once_with(
            f"{settings.KEYCLOAK_INTERNAL_URL.rstrip('/')}"
            f"/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        )

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_rechaza_token_expirado(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        token = self.crear_token(exp=int(time.time()) - 30)

        with self.assertRaises(ExpiredSignatureError):
            validar_access_token(token)

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_rechaza_firma_incorrecta(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        otra_clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        claims = {
            "sub": "usuario-keycloak-1",
            "iss": settings.KEYCLOAK_EXPECTED_ISSUER,
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "azp": settings.KEYCLOAK_CLIENT_ID,
            "email_verified": True,
        }
        token = jwt.encode(claims, otra_clave, algorithm="RS256")

        with self.assertRaises(InvalidSignatureError):
            validar_access_token(token)

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_acepta_cliente_en_aud_sin_azp(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        token = self.crear_token(azp=None, aud=[settings.KEYCLOAK_CLIENT_ID])

        claims = validar_access_token(token)

        self.assertIn(settings.KEYCLOAK_CLIENT_ID, claims["aud"])

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_rechaza_issuer_incorrecto(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        token = self.crear_token(iss="http://keycloak:8080/realms/global-exchange")

        with self.assertRaises(InvalidIssuerError):
            validar_access_token(token)

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_rechaza_cliente_incorrecto(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        token = self.crear_token(azp="otro-cliente", aud=["account"])

        with self.assertRaises(InvalidAudienceError):
            validar_access_token(token)

    @patch("usuarios.services.keycloak._obtener_cliente_jwks")
    def test_rechaza_cuenta_no_verificada(self, mock_jwks):
        mock_jwks.return_value.get_signing_key_from_jwt.return_value.key = (
            self.public_key
        )
        token = self.crear_token(email_verified=False)

        with self.assertRaises(InvalidTokenError):
            validar_access_token(token)


class ConfiguracionRealmTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ruta = Path(settings.BASE_DIR) / "keycloak" / "global-exchange-realm.json"
        cls.realm = json.loads(ruta.read_text(encoding="utf-8"))

    def test_registro_y_verificacion_email_estan_habilitados(self):
        self.assertTrue(self.realm["registrationAllowed"])
        self.assertTrue(self.realm["verifyEmail"])
        self.assertFalse(self.realm["duplicateEmailsAllowed"])
        verify_email = next(
            action
            for action in self.realm["requiredActions"]
            if action["alias"] == "VERIFY_EMAIL"
        )
        self.assertTrue(verify_email["enabled"])

    def test_smtp_apunta_a_mailpit(self):
        self.assertEqual(self.realm["smtpServer"]["host"], "mailpit")
        self.assertEqual(self.realm["smtpServer"]["port"], "1025")

    def test_usuario_es_unico_rol_de_negocio_asignado_por_defecto(self):
        default_role = next(
            role
            for role in self.realm["roles"]["realm"]
            if role["name"] == "default-roles-global-exchange"
        )
        roles_por_defecto = set(default_role["composites"]["realm"])

        self.assertIn("USUARIO", roles_por_defecto)
        self.assertTrue(
            roles_por_defecto.isdisjoint(
                {"ADMINISTRADOR", "CAJERO", "ANALISTA_CAMBIARIO"}
            )
        )

    def test_cliente_exige_pkce_s256(self):
        cliente = next(
            client
            for client in self.realm["clients"]
            if client["clientId"] == "global-exchange-web"
        )

        self.assertEqual(
            cliente["attributes"]["pkce.code.challenge.method"], "S256"
        )

    def test_registro_exige_password_en_formulario_inicial(self):
        registration_form = next(
            flow
            for flow in self.realm["authenticationFlows"]
            if flow["alias"] == "registration form"
        )
        password_validation = next(
            execution
            for execution in registration_form["authenticationExecutions"]
            if execution.get("authenticator") == "registration-password-action"
        )

        self.assertEqual(password_validation["requirement"], "REQUIRED")
        config_alias = password_validation["authenticatorConfig"]
        password_config = next(
            config
            for config in self.realm["authenticatorConfig"]
            if config["alias"] == config_alias
        )
        self.assertEqual(
            password_config["config"]["always_set_password_on_register_form"],
            "true",
        )

class AsignarRolTests(TestCase):
    def _autenticar_como(self, roles):
        session = self.client.session
        session[SESSION_AUTENTICADO] = True
        session[SESSION_USUARIO] = {
            "sub": "admin-prueba",
            "username": "admin",
            "email": "admin@prueba.com",
        }
        session[SESSION_ROLES] = roles
        session[SESSION_EXPIRA_EN] = time.time() + 3600
        session.save()

    def test_requiere_autenticacion(self):
        response = self.client.post(
            reverse("usuarios:asignar_rol"),
            data={
                "usuario_id": "usuario-1",
                "rol": "CAJERO",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_requiere_rol_administrador(self):
        self._autenticar_como(["USUARIO"])

        response = self.client.post(
            reverse("usuarios:asignar_rol"),
            data={
                "usuario_id": "usuario-1",
                "rol": "CAJERO",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("usuarios.views.asignar_rol_usuario")
    def test_administrador_puede_asignar_rol(self, mock_asignar):
        self._autenticar_como(["ADMINISTRADOR"])

        response = self.client.post(
            reverse("usuarios:asignar_rol"),
            data={
                "usuario_id": "usuario-1",
                "rol": "CAJERO",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        mock_asignar.assert_called_once_with("usuario-1", "CAJERO")

    @patch("usuarios.views.asignar_rol_usuario")
    def test_no_permite_rol_duplicado(self, mock_asignar):
        self._autenticar_como(["ADMINISTRADOR"])
        mock_asignar.side_effect = ValueError("El usuario ya posee ese rol.")

        response = self.client.post(
            reverse("usuarios:asignar_rol"),
            data={
                "usuario_id": "usuario-1",
                "rol": "CAJERO",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "El usuario ya posee ese rol.",
        )
