from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_clientes, name='inicio_clientes'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
]