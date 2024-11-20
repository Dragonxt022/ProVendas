# configuracoes/context_processors.py

from .models import Configuracao
from django.utils import timezone
from licencas.models import LicenseKey
from caixa.models import Caixa

def license_days_remaining(request):
    days_remaining = 0
    # Buscar qualquer chave ativa, independentemente do usuário
    active_license = LicenseKey.objects.filter(status='ATIVADO').order_by('-created_at').first()

    if active_license:
        print(f"Expiration Date: {active_license.expiration_date}")
        print(f"Current Date and Time: {timezone.now()}")
        if active_license.expiration_date > timezone.now():
            days_remaining = (active_license.expiration_date - timezone.now()).days
        else:
            days_remaining = -1  # Caso a licença tenha expirado

    return {'days_remaining': days_remaining}



def configuracoes(request):
    # Aqui você recupera as configurações para serem usadas em todos os templates
    configuracao, created = Configuracao.objects.get_or_create(id=1)

    # Busca o caixa aberto para o usuário atual
    caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()

    # Define se o caixa está aberto e passa mais informações se necessário
    caixa_esta_aberto = caixa_aberto is not None
    status_caixa = caixa_aberto.status if caixa_aberto else 'N/D'

    
    return {
        'nome_aplicacao': configuracao.nome_aplicacao,
        'cliente_padrao': configuracao.cliente_padrao,
        'cor_primaria': configuracao.cor_primaria,
        'cor_secundaria': configuracao.cor_secundaria,
        'logo_empresa': configuracao.logo_empresa.url if configuracao.logo_empresa else None,
        'icone_aplicacao': configuracao.icone_aplicacao.url if configuracao.icone_aplicacao else None,
        'gerar_codigo_barra_automatico': configuracao.gerar_codigo_barra_automatico,
        'gerenciar_abertura_fechamento_caixa': configuracao.gerenciar_abertura_fechamento_caixa,
        'caixa_esta_aberto': caixa_esta_aberto,
        'status_caixa': status_caixa,
    }
