# caixa/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_caixa, name='listar_caixa'),
    path('abrir-caixa', views.abrir_caixa_pdv, name='abrir_caixa_pdv'),
    path('clients/search', views.search_client, name='search_client'),
    path('products/search', views.search_products, name='search_products'),
    path('finalizar_venda/', views.finalizar_venda, name='finalizar_venda'),
    path('buscar/venda/<int:id>/', views.get_venda_details, name='admin.caixa.idVenda'),
    path('excluir_venda/', views.excluir_venda, name='excluir_venda'),
    path('cupom_fiscal/<int:pedido_id>/', views.gerar_cupom_fiscal, name='gerar_cupom_fiscal'),
    path('listar-pedidos-ajax/', views.listar_pedidos_ajax, name='listar_pedidos_ajax'),

    

]
