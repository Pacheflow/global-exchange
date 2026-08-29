from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


def registro(request):
    """
    Redirige al usuario al formulario de registro administrado por Keycloak.
    """
    registration_endpoint = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/"
        f"{settings.KEYCLOAK_REALM}/protocol/openid-connect/registrations"
    )

    params = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "response_type": "code",
        "scope": "openid",
        "redirect_uri": "http://localhost:8000/",
    }

    keycloak_registration_url = f"{registration_endpoint}?{urlencode(params)}"

    return redirect(keycloak_registration_url)
