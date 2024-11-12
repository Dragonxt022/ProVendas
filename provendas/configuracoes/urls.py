# configuracoes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_configuracao, name='listar_configuracao'),
]
