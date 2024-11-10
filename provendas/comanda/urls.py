# comanda/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_mesas, name='listar_mesas'),
    path('cadastrar/', views.cadastrar_mesa, name='cadastrar_mesa'),
    path('excluir/<int:mesa_id>/', views.excluir_mesa, name='excluir_mesa'),
    path('abrir-ou-gerenciar-comanda/<int:mesa_id>/', views.abrir_ou_gerenciar_comanda, name='abrir_ou_gerenciar_comanda'),
    path('buscar-produto/<int:mesa_id>/', views.get_comanda_details, name='get_comanda_details'),
    path('adicionar-produto/<int:mesa_id>/', views.adicionar_produto_comanda, name='adicionar_produto_comanda'),
    path('fechar-comanda/<int:mesa_id>/', views.fechar_comanda, name='fechar_comanda'),
    path('historico-vendas/', views.historico_vendas, name='historico_vendas'),
    path('detalhes_comanda/<int:comanda_id>/', views.detalhes_comanda, name='detalhes_comanda'),
    path('excluir/comanda/<int:comanda_id>/', views.excluir_comanda, name='excluir_comanda'),

]
