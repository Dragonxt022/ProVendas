# provendas/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o usuário está autenticado, mas não redireciona para o login se já estiver na página de login
        if not request.user.is_authenticated and request.path != reverse('login'):
            # Redireciona para a página de login
            return redirect(reverse('login'))
        
        response = self.get_response(request)
        return response
