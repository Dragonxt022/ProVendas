# analytics/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.analytics_desboard), name='analytics_desboard'),
    path('filtros-avancados', login_required(views.filtro_relatorio_produtos), name='filtro_relatorio_produtos'),
]