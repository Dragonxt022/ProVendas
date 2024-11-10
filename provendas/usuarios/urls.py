# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/cadastra-atualiza-usuario/', views.cadastrar_atualizar_usuario, name='cadastrar_atualizar_usuario'),
    path('usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
]
