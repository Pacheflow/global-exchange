from django.shortcuts import render, redirect
from .forms import ClienteForm


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