# analytics/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_desboard, name='analytics_desboard'),
]