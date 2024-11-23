import subprocess
from .models import Configuracao
from django.utils import timezone
from django.utils.timezone import now
from licencas.models import LicenseKey
from caixa.models import Caixa
from datetime import datetime

def get_git_commits():
    try:
        result = subprocess.run(['git', 'log', '--oneline', '--max-count=5'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            commits = result.stdout.splitlines()
            formatted_commits = []
            
            # Itera sobre cada commit
            for commit in commits:
                commit_hash, commit_message = commit.split(" ", 1)
                
                # Obtém a data e hora do commit
                commit_datetime = subprocess.run(
                    ['git', 'log', '--format=%cd', '--max-count=1', '--date=iso', commit_hash],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                ).stdout.strip()
                
                # Formatar a data e hora para 'd/m/yy H:M'
                commit_date_obj = datetime.strptime(commit_datetime, '%Y-%m-%d %H:%M:%S %z')  # Converte para datetime
                formatted_date = commit_date_obj.strftime('%d/%m/%y %H:%M')  # Formato 'dd/mm/yy HH:MM'
                
                formatted_commits.append({
                    'commit_hash': commit_hash,
                    'commit_message': commit_message,  # A mensagem já vem corretamente formatada
                    'commit_date': formatted_date
                })
            
            return formatted_commits
        else:
            return []
    except Exception as e:
        print(f"Erro ao obter commits: {e}")
        return []
    
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
    

    # Verifica se o usuário está autenticado antes de buscar o caixa
    if request.user.is_authenticated:
        caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()
        caixa_esta_aberto = caixa_aberto is not None
        status_caixa = caixa_aberto.status if caixa_aberto else 'N/D'
        abrir_caixa_automatico = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False
        
    else:
        caixa_aberto = None
        caixa_esta_aberto = False
        status_caixa = 'N/D'
        abrir_caixa_automatico= None


    # Notificações - Exemplo, ajustando para sua lógica de notificação de licenças
    license_info = license_days_remaining(request)
    days_remaining = license_info['days_remaining']

    notificacoes = []
    if days_remaining == -1:
        notificacoes.append({
            'mensagem': 'Licença expirada!',
            'icone': 'fas fa-exclamation-triangle',
            'cor': '#FFD43B',
            'quantidade': 1
        })
    elif days_remaining <= 7:
        notificacoes.append({
            'mensagem': f'Licença expira em {days_remaining} dias!',
            'icone': 'fas fa-exclamation-circle',
            'cor': '#FF4500',
            'quantidade': 1
        })

     # Obter commits
    commits = get_git_commits()
    if commits:
        for commit in commits:
            notificacoes.append({
                'mensagem': f'{commit["commit_message"]}',
                'data': commit['commit_date'],  # Usando a data formatada
                'icone': 'fas fa-code-branch',
                'cor': '#28A745',
                'quantidade': 1
            })

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
        'abrir_caixa_automatico': abrir_caixa_automatico,
        'status_caixa': status_caixa,
        'notificacoes': notificacoes,
    }
