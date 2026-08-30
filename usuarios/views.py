import base64
import hashlib
import secrets
from urllib.parse import urlencode

import requests
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


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

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "code": code,
        "redirect_uri": "http://localhost:8000/usuarios/callback/",
        "code_verifier": request.session.get("code_verifier"),
    }

    response = requests.post(
        token_endpoint,
        data=data,
        timeout=10,
    )

    if response.status_code != 200:
        return JsonResponse(
            {
                "error": "No se pudo autenticar con Keycloak",
                "details": response.json(),
            },
            status=400,
        )

    tokens = response.json()

    access_token = tokens.get("access_token")

    roles = []

    if access_token:
        try:
            decoded_token = jwt.decode(
                access_token,
                options={"verify_signature": False},
            )

            roles = decoded_token.get("realm_access", {}).get("roles", [])

        except jwt.DecodeError:
            roles = []

    request.session["roles"] = roles

    return JsonResponse(
        {
            "message": "Login exitoso",
            "access_token": access_token,
            "roles": roles,
        }
    )
