"""Cliente mínimo OpenID Connect para el realm de Global Exchange."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class KeycloakError(Exception):
    """Error controlado al comunicarse con Keycloak."""


def endpoint(path=""):
    base = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}"
    return f"{base}{path}"


def _request(url, *, method="GET", data=None, token=None):
    headers = {"Accept": "application/json"}
    body = urlencode(data).encode() if data is not None else None
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, data=body, headers=headers, method=method), timeout=8) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("errorMessage")
        except (ValueError, AttributeError):
            detail = None
        raise KeycloakError(detail or "Keycloak rechazó la operación.") from exc
    except URLError as exc:
        raise KeycloakError("No se pudo conectar con Keycloak. Verificá que esté iniciado.") from exc


def exchange_code(code, redirect_uri):
    return _request(endpoint("/protocol/openid-connect/token"), method="POST", data={
        "grant_type": "authorization_code", "client_id": settings.KEYCLOAK_CLIENT_ID,
        "code": code, "redirect_uri": redirect_uri,
    })


def userinfo(access_token):
    return _request(endpoint("/protocol/openid-connect/userinfo"), token=access_token)


def admin_request(path, token, *, method="GET", payload=None):
    """Llama a Admin REST API con los permisos del usuario autenticado."""
    url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/admin/realms/{settings.KEYCLOAK_REALM}{path}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    body = json.dumps(payload).encode() if payload is not None else None
    if body:
        headers["Content-Type"] = "application/json"
    try:
        with urlopen(Request(url, data=body, headers=headers, method=method), timeout=8) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("errorMessage")
        except (ValueError, AttributeError):
            detail = None
        raise KeycloakError(detail or "No tenés permisos para administrar usuarios.") from exc
    except URLError as exc:
        raise KeycloakError("No se pudo conectar con Keycloak.") from exc
