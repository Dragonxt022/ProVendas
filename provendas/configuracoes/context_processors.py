# configuracoes/context_processors.py

from .models import Configuracao
from django.utils import timezone
from licencas.models import LicenseKey

def license_days_remaining(request):
    days_remaining = 0
    if request.user.is_authenticated:
        # Buscar a chave ativa mais recente do usuário
        active_license = LicenseKey.objects.filter(user=request.user, status='ATIVADO').order_by('-created_at').first()
        
        # Verificar se a chave existe e está ativa
        if active_license and active_license.expiration_date > timezone.now():
            # Calcular os dias restantes até a expiração
            days_remaining = (active_license.expiration_date - timezone.now()).days
        elif active_license and active_license.expiration_date <= timezone.now():
            # Caso a chave esteja expirada, definir dias restantes como 0
            days_remaining = -1  # Licença expirada
    return {'days_remaining': days_remaining}


def configuracoes(request):
    # Aqui você recupera as configurações para serem usadas em todos os templates
    configuracao, created = Configuracao.objects.get_or_create(id=1)  # Supondo que há apenas uma configuração
    
    return {
        'nome_aplicacao': configuracao.nome_aplicacao,
        'cliente_padrao': configuracao.cliente_padrao,
        'cor_primaria': configuracao.cor_primaria,
        'cor_secundaria': configuracao.cor_secundaria,
        'logo_empresa': configuracao.logo_empresa.url if configuracao.logo_empresa else None,
        'icone_aplicacao': configuracao.icone_aplicacao.url if configuracao.icone_aplicacao else None,
    }
