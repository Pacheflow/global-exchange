import secrets
from functools import wraps
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from .keycloak import KeycloakError, admin_request, endpoint, exchange_code, userinfo


def _absolute(request, name):
    return request.build_absolute_uri(reverse(name))


def _auth_url(request, registration=False):
    state = secrets.token_urlsafe(32)
    request.session["oidc_state"] = state
    action = "registrations" if registration else "auth"
    params = {"client_id": settings.KEYCLOAK_CLIENT_ID, "response_type": "code",
              "scope": "openid profile email roles", "redirect_uri": _absolute(request, "usuarios:callback"), "state": state}
    return f"{endpoint('/protocol/openid-connect/' + action)}?{urlencode(params)}"


def oidc_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.session.get("kc_user"):
            request.session["next"] = request.get_full_path()
            messages.info(request, "Iniciá sesión para continuar.")
            return redirect("usuarios:login")
        return view(request, *args, **kwargs)
    return wrapped


def home(request):
    return render(request, "usuarios/home.html")


def login(request):
    return redirect(_auth_url(request))


def registro(request):
    return redirect(_auth_url(request, True))


def callback(request):
    if request.GET.get("error"):
        messages.error(request, "Keycloak canceló o rechazó el acceso.")
        return redirect("usuarios:home")
    expected = request.session.pop("oidc_state", "")
    if not expected or not secrets.compare_digest(request.GET.get("state", ""), expected):
        return HttpResponseBadRequest("Estado OIDC inválido. Volvé a iniciar sesión.")
    if not request.GET.get("code"):
        return HttpResponseBadRequest("Keycloak no devolvió el código de autorización.")
    try:
        tokens = exchange_code(request.GET["code"], _absolute(request, "usuarios:callback"))
        profile = userinfo(tokens["access_token"])
    except KeycloakError as exc:
        messages.error(request, str(exc))
        return redirect("usuarios:home")
    request.session.cycle_key()
    request.session["kc_user"] = profile
    request.session["kc_access_token"] = tokens["access_token"]
    request.session["kc_id_token"] = tokens.get("id_token")
    messages.success(request, f"¡Hola, {profile.get('given_name') or profile.get('preferred_username')}!")
    return redirect(request.session.pop("next", "usuarios:dashboard"))


def logout(request):
    hint = request.session.get("kc_id_token")
    request.session.flush()
    params = {"client_id": settings.KEYCLOAK_CLIENT_ID, "post_logout_redirect_uri": _absolute(request, "usuarios:home")}
    if hint:
        params["id_token_hint"] = hint
    return redirect(f"{endpoint('/protocol/openid-connect/logout')}?{urlencode(params)}")


@oidc_required
def dashboard(request):
    return render(request, "usuarios/dashboard.html")


@oidc_required
def usuarios(request):
    try:
        rows, error = admin_request("/users?max=100", request.session["kc_access_token"]), None
    except KeycloakError as exc:
        rows, error = [], str(exc)
    return render(request, "usuarios/user_list.html", {"users": rows, "api_error": error})


@oidc_required
def crear_usuario(request):
    if request.method == "POST":
        password = request.POST.get("password", "")
        payload = {"username": request.POST.get("username", "").strip(), "email": request.POST.get("email", "").strip(),
                   "firstName": request.POST.get("first_name", "").strip(), "lastName": request.POST.get("last_name", "").strip(),
                   "enabled": True, "emailVerified": False,
                   "credentials": [{"type": "password", "value": password, "temporary": True}]}
        if not payload["username"] or not payload["email"] or len(password) < 8:
            messages.error(request, "Completá usuario, email y una contraseña de al menos 8 caracteres.")
        else:
            try:
                admin_request("/users", request.session["kc_access_token"], method="POST", payload=payload)
                messages.success(request, "Usuario creado. Deberá cambiar su contraseña al ingresar.")
                return redirect("usuarios:list")
            except KeycloakError as exc:
                messages.error(request, str(exc))
    return render(request, "usuarios/user_form.html", {"mode": "create"})


@oidc_required
def editar_usuario(request, user_id):
    try:
        user = admin_request(f"/users/{user_id}", request.session["kc_access_token"])
        if request.method == "POST":
            user.update({"email": request.POST.get("email", "").strip(), "firstName": request.POST.get("first_name", "").strip(),
                         "lastName": request.POST.get("last_name", "").strip(), "enabled": request.POST.get("enabled") == "on"})
            admin_request(f"/users/{user_id}", request.session["kc_access_token"], method="PUT", payload=user)
            messages.success(request, "Usuario actualizado.")
            return redirect("usuarios:list")
    except KeycloakError as exc:
        messages.error(request, str(exc))
        return redirect("usuarios:list")
    return render(request, "usuarios/user_form.html", {"mode": "edit", "managed_user": user})


@oidc_required
def baja_usuario(request, user_id):
    if request.method == "POST":
        try:
            user = admin_request(f"/users/{user_id}", request.session["kc_access_token"])
            user["enabled"] = False
            admin_request(f"/users/{user_id}", request.session["kc_access_token"], method="PUT", payload=user)
            messages.success(request, "Usuario dado de baja; sus datos fueron conservados.")
        except KeycloakError as exc:
            messages.error(request, str(exc))
    return redirect("usuarios:list")


@oidc_required
def clientes(request):
    raw = request.session["kc_user"].get("clientes") or request.session["kc_user"].get("client_ids") or []
    if isinstance(raw, str):
        raw = [value.strip() for value in raw.split(",") if value.strip()]
    available = [{"id": value, "name": value.replace("-", " ").title()} for value in raw]
    if request.method == "POST":
        chosen = request.POST.get("cliente")
        if chosen not in {item["id"] for item in available}:
            messages.error(request, "Ese cliente no está asociado a tu usuario.")
        else:
            request.session["selected_client"] = next(item for item in available if item["id"] == chosen)
            messages.success(request, "Contexto de cliente actualizado.")
            return redirect("usuarios:dashboard")
    return render(request, "usuarios/client_select.html", {"clients": available})
