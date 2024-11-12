# configuracoes/context_processors.py

from .models import Configuracao

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
