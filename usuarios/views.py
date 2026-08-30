import base64
import hashlib
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from jwt.exceptions import InvalidTokenError

from .decorators import requiere_autenticacion, requiere_rol
from .services.keycloak import (
    SESSION_ROLES,
    SESSION_USUARIO,
    establecer_sesion_oidc,
    limpiar_sesion_oidc,
    validar_access_token,
)


def registro(request):
    """
    Redirige al usuario al formulario de registro administrado por Keycloak.
    """

    code_verifier = secrets.token_urlsafe(64)

    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .replace("=", "")
    )

    request.session["code_verifier"] = code_verifier

    registration_endpoint = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/"
        f"{settings.KEYCLOAK_REALM}/protocol/openid-connect/registrations"
    )

    params = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": "http://localhost:8000/",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    keycloak_registration_url = f"{registration_endpoint}?{urlencode(params)}"

    return redirect(keycloak_registration_url)


def login(request):
    """
    Inicia sesión utilizando Keycloak mediante Authorization Code Flow + PKCE.
    """

    code_verifier = secrets.token_urlsafe(64)

    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .replace("=", "")
    )

    request.session["code_verifier"] = code_verifier

    authorization_endpoint = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/"
        f"{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    )

    params = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": "http://localhost:8000/usuarios/callback/",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    login_url = f"{authorization_endpoint}?{urlencode(params)}"

    return redirect(login_url)


def callback(request):
    """
    Recibe la respuesta de Keycloak después del login.
    """

    code = request.GET.get("code")

    if not code:
        return JsonResponse(
            {"error": "No se recibió código de autorización"},
            status=400,
        )

    token_endpoint = (
        f"{settings.KEYCLOAK_INTERNAL_URL}/realms/"
        f"{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    )

    code_verifier = request.session.pop("code_verifier", None)

    if not code_verifier:
        limpiar_sesion_oidc(request)
        return JsonResponse(
            {"error": "No se encontró un flujo de autenticación válido"},
            status=400,
        )

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "code": code,
        "redirect_uri": "http://localhost:8000/usuarios/callback/",
        "code_verifier": code_verifier,
    }

    try:
        response = requests.post(
            token_endpoint,
            data=data,
            timeout=10,
        )
    except requests.RequestException:
        limpiar_sesion_oidc(request)
        return JsonResponse(
            {"error": "Keycloak no está disponible"},
            status=502,
        )

    if response.status_code != 200:
        limpiar_sesion_oidc(request)
        return JsonResponse(
            {"error": "No se pudo autenticar con Keycloak"},
            status=400,
        )

    try:
        tokens = response.json()
        claims = validar_access_token(tokens.get("access_token"))
    except (ValueError, InvalidTokenError):
        limpiar_sesion_oidc(request)
        return JsonResponse(
            {"error": "Keycloak devolvió un token inválido"},
            status=400,
        )

    establecer_sesion_oidc(request, claims)

    return JsonResponse(
        {
            "message": "Login exitoso",
            "usuario": request.session[SESSION_USUARIO],
            "roles": request.session[SESSION_ROLES],
        }
    )


@requiere_autenticacion
def perfil_usuario(request):
    """
    Devuelve la información del usuario autenticado y sus roles.
    """

    return JsonResponse(
        {
            "usuario": request.session[SESSION_USUARIO],
            "roles": request.session[SESSION_ROLES],
        }
    )


@requiere_rol("ADMINISTRADOR")
def acceso_administrador(request):
    """Vista mínima para comprobar autorización backend por rol."""

    return JsonResponse(
        {
            "message": "Acceso administrativo permitido",
            "usuario": request.session[SESSION_USUARIO],
        }
    )
