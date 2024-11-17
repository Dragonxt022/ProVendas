from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar_categoria/', views.cadastrar_categoria, name='cadastrar_categoria'),
    path('cadastrar_categoria_ajax/', views.cadastrar_categoria_ajax, name='cadastrar_categoria_ajax'), 

    path('listar_categorias/', views.listar_categorias, name='listar_categorias'),
    path('excluir_categoria/<int:categoria_id>/', (views.excluir_categoria), name='excluir_categoria'),

    # rotas dos produtos
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/editar_produto/<int:produto_id>/', views.editar_produto, name='editar_produto'),  
    path('produtos/excluir_produto/<int:produto_id>/', views.excluir_produto, name='excluir_produto'),  

    # Importador
    path('importar/', views.importar_produtos, name='importar_produtos'),
    path('exportar/', views.exportar_produtos, name='exportar_produtos'),
]

