from functools import wraps

from django.http import JsonResponse


def requiere_rol(rol_requerido):
    """
    Verifica que el usuario autenticado tenga un rol específico.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            roles = request.session.get("roles", [])

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
