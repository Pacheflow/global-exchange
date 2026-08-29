from django.shortcuts import render, redirect
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
            form.save()
            return redirect("inicio_clientes")

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