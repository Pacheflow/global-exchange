from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("login/", views.login, name="login"),
    path("callback/", views.callback, name="callback"),
    path("perfil/", views.perfil_usuario, name="perfil_usuario"),
    path(
        "acceso-administrador/",
        views.acceso_administrador,
        name="acceso_administrador",
    ),
    path("asignar-rol/", views.asignar_rol, name="asignar_rol"),
]
