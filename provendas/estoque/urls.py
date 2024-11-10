from django.urls import path
from .views import (
    cadastrar_categoria,
    listar_categorias,
    excluir_categoria,
    listar_produtos,
    editar_produto,
    excluir_produto,
    importar_produtos,
    exportar_produtos,

)

urlpatterns = [
    path('cadastrar_categoria/', cadastrar_categoria, name='cadastrar_categoria'),
    path('listar_categorias/', listar_categorias, name='listar_categorias'),
    path('excluir_categoria/<int:categoria_id>/', excluir_categoria, name='excluir_categoria'),

    # rotas dos produtos
    path('produtos/', listar_produtos, name='listar_produtos'),
    path('produtos/editar_produto/<int:produto_id>/', editar_produto, name='editar_produto'),  # Removido 'estoque/' do caminho
    path('produtos/excluir_produto/<int:produto_id>/', excluir_produto, name='excluir_produto'),  # Atualizado para manter a consistência

    #  Importador
    path('importar/', importar_produtos, name='importar_produtos'),
    path('exportar/', exportar_produtos, name='exportar_produtos'),
]
