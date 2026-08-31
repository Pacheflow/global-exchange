from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.inicio_clientes,
        name='inicio_clientes'
    ),

    path(
        'registrar/',
        views.registrar_cliente,
        name='registrar_cliente'
    ),

    path(
        'consultar/',
        views.consultar_clientes,
        name='consultar_clientes'
    ),

    path(
        'editar/<int:cliente_id>/',
        views.editar_cliente,
        name='editar_cliente'
    ),

    path(
        'baja/<int:cliente_id>/',
        views.dar_de_baja_cliente,
        name='dar_de_baja_cliente'
    ),

    path(
        'segmentar/<int:cliente_id>/',
        views.segmentar_cliente,
        name='segmentar_cliente'
    ),
    path(
        'seleccionar/<int:cliente_id>/',
        views.seleccionar_cliente,
        name='seleccionar_cliente'
    ),
    path(
        'deseleccionar/',
        views.deseleccionar_cliente,
        name='deseleccionar_cliente'
    ),
    path(
        '<int:cliente_id>/usuarios/',
        views.asignaciones_cliente,
        name='asignaciones_cliente'
    ),
    path(
        '<int:cliente_id>/usuarios/<int:asignacion_id>/quitar/',
        views.quitar_asignacion_cliente,
        name='quitar_asignacion_cliente'
    ),
]
