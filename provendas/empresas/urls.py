# empresas/urls.py

from django.urls import path
from .views import Empresa
from . import views

urlpatterns = [
    path('listar_empresas/', views.listar_empresas, name='listar_empresas'),
    path('excluir_empresa/<int:empresa_id>/', views.excluir_empresa, name='excluir_empresa'),

]
