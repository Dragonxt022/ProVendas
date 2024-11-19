# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
]
