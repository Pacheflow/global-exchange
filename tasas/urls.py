from django.urls import path

from . import views


app_name = "tasas"

urlpatterns = [
    path("", views.consultar_tasas, name="consultar"),
]
