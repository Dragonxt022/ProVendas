# analytics/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_desboard, name='analytics_desboard'),
    path('filtros-avancados', views.filtro_relatorio_produtos, name='filtro_relatorio_produtos'),
]