from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ClienteForm, SegmentacionClienteForm
from .models import Cliente

def inicio_clientes(request):
    """Muestra la pantalla principal del módulo de clientes."""
    return render(request, "clientes/inicio.html")


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
def consultar_clientes(request):
    """Muestra y permite buscar los clientes registrados."""

    busqueda = request.GET.get("buscar", "")

    clientes = Cliente.objects.all()

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
def editar_cliente(request, cliente_id):
    """Permite modificar los datos de un cliente registrado."""

    cliente = Cliente.objects.filter(id=cliente_id).first()

    if cliente is None:
        return render(
            request,
            "clientes/editar.html",
            {"cliente_no_encontrado": True}
        )

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
def dar_de_baja_cliente(request, cliente_id):
    """Permite dar de baja lógicamente a un cliente."""

    cliente = Cliente.objects.filter(id=cliente_id).first()

    if cliente is None:
        return render(
            request,
            "clientes/baja.html",
            {"cliente_no_encontrado": True}
        )

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
def segmentar_cliente(request, cliente_id):
    """Permite asignar o modificar la categoría de un cliente."""

    cliente = Cliente.objects.filter(id=cliente_id).first()

    if cliente is None:
        return render(
            request,
            "clientes/segmentar.html",
            {"cliente_no_encontrado": True}
        )

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


def seleccionar_cliente(request, cliente_id):
    """Define el cliente activo utilizado como contexto de trabajo."""

    if request.method == "POST":
        cliente = get_object_or_404(Cliente, id=cliente_id, estado="ACTIVO")
        request.session["selected_client"] = {
            "id": cliente.id,
            "name": cliente.nombre_razon_social,
        }
        messages.success(request, f"Ahora estás trabajando con {cliente.nombre_razon_social}.")
        return redirect("usuarios:dashboard")
    return redirect("consultar_clientes")
