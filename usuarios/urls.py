from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("registro/", views.registro, name="registro"),
    path("callback/", views.callback, name="callback"),
    path("logout/", views.logout, name="logout"),
    path("panel/", views.dashboard, name="dashboard"),
    path("usuarios/", views.usuarios, name="list"),
    path("usuarios/nuevo/", views.crear_usuario, name="create"),
    path("usuarios/<str:user_id>/editar/", views.editar_usuario, name="edit"),
    path("usuarios/<str:user_id>/baja/", views.baja_usuario, name="disable"),
    path("clientes/seleccionar/", views.clientes, name="clients"),
]
