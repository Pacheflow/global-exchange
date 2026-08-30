from functools import lru_cache

import jwt
from django.conf import settings
from jwt import PyJWKClient
from jwt.exceptions import (
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidTokenError,
    PyJWKClientError,
)


ROLES_SISTEMA = frozenset(
    {
        "ADMINISTRADOR",
        "CAJERO",
        "ANALISTA_CAMBIARIO",
        "USUARIO",
    }
)

SESSION_AUTENTICADO = "oidc_authenticated"
SESSION_USUARIO = "oidc_user"
SESSION_ROLES = "roles"

ALGORITMOS_PERMITIDOS = ("RS256",)


def _realm_url(base_url):
    return f"{base_url.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}"


@lru_cache(maxsize=4)
def _obtener_cliente_jwks(jwks_url):
    return PyJWKClient(jwks_url)


def extraer_roles_sistema(claims):
    """Devuelve únicamente los roles de negocio definidos por Global Exchange."""

    realm_access = claims.get("realm_access", {})
    if not isinstance(realm_access, dict):
        return []

    roles_token = realm_access.get("roles", [])

    if not isinstance(roles_token, list):
        return []

    return sorted(set(roles_token).intersection(ROLES_SISTEMA))


def validar_access_token(access_token):
    """Valida firma y claims mínimos de un access token emitido por Keycloak."""

    if not access_token:
        raise InvalidTokenError("Keycloak no devolvió un access token.")

    header = jwt.get_unverified_header(access_token)
    algoritmo = header.get("alg")

    if algoritmo not in ALGORITMOS_PERMITIDOS:
        raise InvalidAlgorithmError("Algoritmo de firma no permitido.")

    issuer = _realm_url(settings.KEYCLOAK_SERVER_URL)
    jwks_url = (
        f"{_realm_url(settings.KEYCLOAK_INTERNAL_URL)}"
        "/protocol/openid-connect/certs"
    )

    try:
        signing_key = _obtener_cliente_jwks(jwks_url).get_signing_key_from_jwt(
            access_token
        )
    except PyJWKClientError as exc:
        raise InvalidTokenError(
            "No fue posible obtener la clave de firma de Keycloak."
        ) from exc

    claims = jwt.decode(
        access_token,
        signing_key.key,
        algorithms=list(ALGORITMOS_PERMITIDOS),
        issuer=issuer,
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": False,
            "require": ["exp", "iat", "iss", "sub"],
        },
        leeway=10,
    )

    audiencias = claims.get("aud", [])
    if isinstance(audiencias, str):
        audiencias = [audiencias]
    elif not isinstance(audiencias, (list, tuple, set)):
        audiencias = []

    cliente_autorizado = (
        claims.get("azp") == settings.KEYCLOAK_CLIENT_ID
        or settings.KEYCLOAK_CLIENT_ID in audiencias
    )

    if not cliente_autorizado:
        raise InvalidAudienceError(
            "El token no fue emitido para el cliente configurado."
        )

    return claims


def establecer_sesion_oidc(request, claims):
    """Crea el contexto de autenticación usado por la autorización backend."""

    request.session.cycle_key()
    request.session[SESSION_AUTENTICADO] = True
    request.session[SESSION_USUARIO] = {
        "sub": claims["sub"],
        "username": claims.get("preferred_username", ""),
        "email": claims.get("email", ""),
    }
    request.session[SESSION_ROLES] = extraer_roles_sistema(claims)


def limpiar_sesion_oidc(request):
    """Elimina cualquier autorización OIDC previa de la sesión."""

    for clave in (SESSION_AUTENTICADO, SESSION_USUARIO, SESSION_ROLES):
        request.session.pop(clave, None)
