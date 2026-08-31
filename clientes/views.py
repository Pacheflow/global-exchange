from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from usuarios.keycloak import KeycloakError, admin_request
from usuarios.decorators import requiere_roles_web

from .forms import AsignacionUsuarioClienteForm, ClienteForm, SegmentacionClienteForm
from .models import Cliente, UsuarioCliente


def _keycloak_user_id(request):
    """Obtiene la identidad externa o rechaza una sesión web inconsistente."""

    user_id = request.session.get("kc_user", {}).get("sub")
    if not user_id:
        raise PermissionDenied("No se encontró una identidad Keycloak válida.")
    return user_id


def _clientes_asignados_a(request, queryset=None):
    """Limita un queryset a las asociaciones activas del usuario autenticado."""

    queryset = queryset if queryset is not None else Cliente.objects.all()
    return queryset.filter(
        usuarios_asignados__keycloak_user_id=_keycloak_user_id(request),
        usuarios_asignados__activo=True,
    )


@requiere_roles_web("ADMINISTRADOR", "CAJERO", "ANALISTA_CAMBIARIO", "USUARIO")
@require_GET
def inicio_clientes(request):
    """Muestra la pantalla principal del módulo de clientes."""
    return render(request, "clientes/inicio.html")


@requiere_roles_web("ADMINISTRADOR")
@require_http_methods(["GET", "POST"])
def registrar_cliente(request):
    """Permite registrar un nuevo cliente en el sistema."""

    if request.method == "POST":
        form = ClienteForm(request.POST)

        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nombre_razon_social} registrado.")
            return redirect("consultar_clientes")

    else:
        form = ClienteForm()

    return render(
        request,
        "clientes/registrar.html",
        {"form": form}
    )


@requiere_roles_web("ADMINISTRADOR", "CAJERO", "ANALISTA_CAMBIARIO", "USUARIO")
@require_GET
def consultar_clientes(request):
    """Muestra y permite buscar los clientes registrados."""

    busqueda = request.GET.get("buscar", "")

    clientes = Cliente.objects.all()
    roles = set(request.session.get("roles", []))
    if "ADMINISTRADOR" not in roles:
        clientes = _clientes_asignados_a(request, clientes)

    if busqueda:
        clientes = clientes.filter(
            nombre_razon_social__icontains=busqueda
        )

    return render(
        request,
        "clientes/consultar.html",
        {
            "clientes": clientes,
            "busqueda": busqueda,
        }
    )


@requiere_roles_web("ADMINISTRADOR")
@require_http_methods(["GET", "POST"])
def editar_cliente(request, cliente_id):
    """Permite modificar los datos de un cliente registrado."""

    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            form.save()
            messages.success(request, "Los datos del cliente fueron actualizados.")
            return redirect("consultar_clientes")

    else:
        form = ClienteForm(instance=cliente)

    return render(
        request,
        "clientes/editar.html",
        {
            "form": form,
            "cliente": cliente,
        }
    )


@requiere_roles_web("ADMINISTRADOR")
@require_http_methods(["GET", "POST"])
def dar_de_baja_cliente(request, cliente_id):
    """Permite dar de baja lógicamente a un cliente."""

    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        cliente.dar_de_baja()
        if request.session.get("selected_client", {}).get("id") == cliente.id:
            request.session.pop("selected_client", None)
        messages.success(request, "Cliente dado de baja correctamente.")
        return redirect("consultar_clientes")

    return render(
        request,
        "clientes/baja.html",
        {"cliente": cliente}
    )


@requiere_roles_web("ADMINISTRADOR", "ANALISTA_CAMBIARIO")
@require_http_methods(["GET", "POST"])
def segmentar_cliente(request, cliente_id):
    """Permite asignar o modificar la categoría de un cliente."""

    roles = set(request.session.get("roles", []))
    clientes_permitidos = Cliente.objects.all()
    if "ADMINISTRADOR" not in roles:
        clientes_permitidos = _clientes_asignados_a(request, clientes_permitidos)
    cliente = get_object_or_404(clientes_permitidos, id=cliente_id)

    if request.method == "POST":
        form = SegmentacionClienteForm(
            request.POST,
            instance=cliente
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Segmentación del cliente actualizada.")
            return redirect("consultar_clientes")

    else:
        form = SegmentacionClienteForm(instance=cliente)

    return render(
        request,
        "clientes/segmentar.html",
        {
            "form": form,
            "cliente": cliente,
        }
    )


@requiere_roles_web("ADMINISTRADOR", "CAJERO", "ANALISTA_CAMBIARIO", "USUARIO")
@require_POST
def seleccionar_cliente(request, cliente_id):
    """Define el cliente activo utilizado como contexto de trabajo."""

    cliente = get_object_or_404(Cliente, id=cliente_id, estado="ACTIVO")
    roles = set(request.session.get("roles", []))
    if "ADMINISTRADOR" not in roles:
        get_object_or_404(
            UsuarioCliente,
            cliente=cliente,
            keycloak_user_id=_keycloak_user_id(request),
            activo=True,
        )
    request.session["selected_client"] = {
        "id": cliente.id,
        "name": cliente.nombre_razon_social,
    }
    messages.success(request, f"Ahora estás trabajando con {cliente.nombre_razon_social}.")
    return redirect("usuarios:dashboard")


@requiere_roles_web("ADMINISTRADOR", "CAJERO", "ANALISTA_CAMBIARIO", "USUARIO")
@require_POST
def deseleccionar_cliente(request):
    """Elimina el contexto de cliente sin modificar el registro del cliente."""

    request.session.pop("selected_client", None)
    messages.success(request, "Ya no hay un cliente seleccionado.")
    return redirect("consultar_clientes")


@requiere_roles_web("ADMINISTRADOR")
@require_http_methods(["GET", "POST"])
def asignaciones_cliente(request, cliente_id):
    """Administra las identidades Keycloak autorizadas para un cliente."""

    cliente = get_object_or_404(Cliente, id=cliente_id)
    try:
        keycloak_users = admin_request("/users?max=200") or []
        api_error = None
    except KeycloakError as exc:
        keycloak_users, api_error = [], str(exc)

    usuarios = [
        {
            "id": user["id"],
            "label": (
                f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
                or user.get("username")
                or user.get("email")
            ),
            "username": user.get("username") or user.get("email") or user["id"],
        }
        for user in keycloak_users
    ]
    lookup = {user["id"]: user for user in usuarios}

    if request.method == "POST":
        form = AsignacionUsuarioClienteForm(request.POST, usuarios=usuarios)
        if form.is_valid():
            user_id = form.cleaned_data["usuario"]
            selected = lookup[user_id]
            assignment, created = UsuarioCliente.objects.update_or_create(
                cliente=cliente,
                keycloak_user_id=user_id,
                defaults={
                    "username": selected["username"],
                    "rol_en_cliente": form.cleaned_data["rol_en_cliente"],
                    "activo": True,
                },
            )
            action = "asignado" if created else "actualizado"
            messages.success(request, f"Usuario {assignment.username} {action}.")
            return redirect("asignaciones_cliente", cliente_id=cliente.id)
    else:
        form = AsignacionUsuarioClienteForm(usuarios=usuarios)

    return render(request, "clientes/asignaciones.html", {
        "cliente": cliente,
        "asignaciones": cliente.usuarios_asignados.filter(activo=True),
        "form": form,
        "api_error": api_error,
    })


@requiere_roles_web("ADMINISTRADOR")
@require_POST
def quitar_asignacion_cliente(request, cliente_id, asignacion_id):
    asignacion = get_object_or_404(
        UsuarioCliente,
        id=asignacion_id,
        cliente_id=cliente_id,
    )
    if request.session.get("selected_client", {}).get("id") == cliente_id:
        current_user = request.session.get("kc_user", {}).get("sub")
        if current_user == asignacion.keycloak_user_id:
            request.session.pop("selected_client", None)
    asignacion.delete()
    messages.success(request, "Asignación eliminada.")
    return redirect("asignaciones_cliente", cliente_id=cliente_id)
