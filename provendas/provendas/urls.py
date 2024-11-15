from django.conf import settings  # Certifique-se de importar as configurações
from django.conf.urls import handler404, handler403, handler500
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.conf.urls.static import static  # Importando para servir arquivos de mídia
from .views import login_view
from django.contrib.auth import views as auth_views




# Define suas views personalizadas
handler404 = TemplateView.as_view(template_name="404.html")
handler403 = TemplateView.as_view(template_name="403.html")
handler500 = TemplateView.as_view(template_name="500.html")


urlpatterns = [
    
    path('', views.home_redirect, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoque/', include('estoque.urls')),
    path('empresas/', include('empresas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('clientes/', include('clientes.urls')),
    path('caixa/', include('caixa.urls')),
    path('comanda/', include('comanda.urls')),
    path('configuracoes/', include('configuracoes.urls')),
    path('analytics/', include('analytics.urls')),
    path('licencas/', include('licencas.urls')),
]

# Adicione o suporte para arquivos de mídia
if settings.DEBUG:  # Apenas em modo de desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
