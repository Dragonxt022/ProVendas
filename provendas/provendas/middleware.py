from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from licencas.models import LicenseKey

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs liberadas da autenticação
        exempt_urls = [
            reverse('generate_license_key'),
            reverse('add_license_key'),
            reverse('verificar_licenca'),
        ]
        
        # Se a URL acessada for uma das isentas, permite continuar sem autenticação
        if request.path_info in exempt_urls:
            return self.get_response(request)

        # Se o usuário não está autenticado e não está tentando acessar as rotas liberadas, redireciona para o login
        if not request.user.is_authenticated and request.path_info != reverse('login'):
            return redirect(reverse('login'))

        # Se o usuário está autenticado, verifica a licença
        if request.user.is_authenticated:
            # Verifica se a URL é a de login para evitar o loop
            if request.path_info == reverse('login'):
                return self.get_response(request)  # Não fazer nada na página de login

            # Busca a licença ativa mais recente, independentemente de usuário
            active_license = LicenseKey.objects.filter(status='ATIVADO').order_by('-created_at').first()

            # Se não há licença ativa ou a licença está expirada
            if not active_license or active_license.expiration_date < timezone.now():
                days_since_expired = (timezone.now() - active_license.expiration_date).days if active_license else 0

                # Se a licença está expirada há 3 dias ou mais, desloga o usuário e redireciona para a página de login
                if days_since_expired >= 3:
                    logout(request)
                    return redirect(reverse('login'))

        response = self.get_response(request)
        return response
