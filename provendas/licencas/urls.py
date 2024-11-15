from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_license_key, name='generate_license_key'),
    path('add_license_key/', views.add_license_key, name='add_license_key'),
    path('verificar-licenca/', views.verificar_licenca, name='verificar_licenca'),


]
