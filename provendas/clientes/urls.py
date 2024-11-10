# clientes/urls.py
from django.urls import path
from .views import cadastrar_cliente, listar_clientes, editar_cliente, excluir_cliente

urlpatterns = [
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/cadastrar-cliente/', cadastrar_cliente, name='cadastrar_cliente'),
    path('cliente/editar-cliente/<int:cliente_id>/', editar_cliente, name='editar_cliente'), 
    path('excluir_cliente/<int:id>/', excluir_cliente, name='excluir_cliente'),

]
