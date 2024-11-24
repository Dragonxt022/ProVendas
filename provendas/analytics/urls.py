# analytics/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.analytics_desboard), name='analytics_desboard'),
    path('relatorio-vendas', login_required(views.relatorio_vendas), name='relatorio_vendas'),
    path('relatorio-vendas-ajax', login_required(views.relatorio_vendas_ajax), name='relatorio_vendas_ajax'),
]