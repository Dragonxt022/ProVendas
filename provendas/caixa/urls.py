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
    path('cupom_fiscal_ajax/<int:pedido_id>/', views.cupom_fiscal_ajax, name='cupom_fiscal_ajax'),
    
    path('abrir_caixa_ajax/', views.abrir_caixa_ajax, name='abrir_caixa_ajax'),
    path('fechar_caixa_ajax/', views.fechar_caixa_ajax, name='fechar_caixa_ajax'),
    path('verificar_caixa_aberto/', views.verificar_caixa_aberto, name='verificar_caixa_aberto'),

    # Ajax
    path('listar-caixas-abertos-ajax/', views.listar_caixas_abertos_ajax, name='listar_caixas_abertos_ajax'),
    path('retirar-ou-adicionar-valor-ajax/', views.retirar_ou_adicionar_valor_ajax, name='retirar_ou_adicionar_valor_ajax'),


    

]
