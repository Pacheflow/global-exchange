from django.shortcuts import render


def inicio_clientes(request):
    return render(request, 'clientes/inicio.html')