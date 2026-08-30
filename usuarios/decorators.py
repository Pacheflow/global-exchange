from functools import wraps

from django.http import JsonResponse

from .services.keycloak import (
    ROLES_SISTEMA,
    SESSION_AUTENTICADO,
    SESSION_ROLES,
    SESSION_USUARIO,
)


def _usuario_oidc_autenticado(request):
    usuario = request.session.get(SESSION_USUARIO, {})
    return (
        request.session.get(SESSION_AUTENTICADO) is True
        and isinstance(usuario, dict)
        and bool(usuario.get("sub"))
    )


def requiere_autenticacion(view_func):
    """Rechaza en backend solicitudes sin una sesión OIDC verificada."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _usuario_oidc_autenticado(request):
            return JsonResponse(
                {"error": "Autenticación requerida"},
                status=401,
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def requiere_rol(rol_requerido):
    """
    Verifica que el usuario autenticado tenga un rol específico.
    """

    if rol_requerido not in ROLES_SISTEMA:
        raise ValueError(f"Rol de sistema desconocido: {rol_requerido}")

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not _usuario_oidc_autenticado(request):
                return JsonResponse(
                    {"error": "Autenticación requerida"},
                    status=401,
                )

            roles = request.session.get(SESSION_ROLES, [])

            if rol_requerido not in roles:
                return JsonResponse(
                    {
                        "error": "Acceso denegado",
                        "rol_requerido": rol_requerido,
                    },
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
