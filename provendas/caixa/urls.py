# caixa/urls.py
from django.urls import path
from .views import listar_caixa, abrir_caixa_pdv, search_client, search_products, finalizar_venda, get_venda_details, excluir_venda

urlpatterns = [
    path('', listar_caixa, name='listar_caixa'),
    path('abrir-caixa', abrir_caixa_pdv, name='abrir_caixa_pdv'),
    path('clients/search', search_client, name='search_client'),
    path('products/search', search_products, name='search_products'),
    path('finalizar_venda/', finalizar_venda, name='finalizar_venda'),
    path('buscar/venda/<int:id>/', get_venda_details, name='admin.caixa.idVenda'),  # Nova rota
    path('excluir_venda/', excluir_venda, name='excluir_venda'),


]
