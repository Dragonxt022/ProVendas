from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from estoque.models import Produto
from django.db.models import Sum, Count
from django.db.models.functions import ExtractHour
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import redirect
from django.contrib.auth import logout
from licencas.models import LicenseKey
from django.utils import timezone





def home_redirect(request):
    return redirect('login')

def custom_logout(request):
    logout(request)  # Encerra a sessão do usuário
    return redirect('login') 


def login_view(request):
    # Verifica se o usuário já está autenticado
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redireciona para o dashboard se o usuário já estiver autenticado

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentica o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verifica a licença antes de logar
            active_license = LicenseKey.objects.filter(status='ATIVADO').order_by('-created_at').first()

            # Se não houver licença ativa ou a licença estiver expirada
            if not active_license or active_license.expiration_date < timezone.now():
                if active_license:
                    days_since_expired = (timezone.now() - active_license.expiration_date).days
                else:
                    days_since_expired = 0
                # Se a licença expirou há 3 dias ou mais
                if days_since_expired >= 3:
                    messages.error(request, "Sua licença expirou há mais de 3 dias. Não é possível acessar o sistema.")
                    return render(request, 'login.html')

            # Caso a licença esteja válida ou dentro do limite de expiração
            login(request, user)
            return redirect('dashboard')  # Redireciona para o painel principal

        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')


def dashboard(request):
    # Pegando o ano e mês da query string ou usando os valores atuais
    ano = int(request.GET.get('ano', now().year))
    mes = int(request.GET.get('mes', now().month))

    # Gerar lista de anos desde 2020 até o ano atual
    ano_atual = datetime.now().year
    anos = list(range(2020, ano_atual + 1))

    # Lista de meses do ano
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    # Dados para os blocos na página principal (index)
    pedidos_finalizados = CaixaPdv.objects.filter(status='Finalizado').count()
    total_vendas_mes = CaixaPdv.objects.filter(
        created_at__month=mes,
        created_at__year=ano
    ).aggregate(Sum('total'))['total__sum'] or 0.00
    total_produtos = ProdutoCaixaPdv.objects.count()
    total_vendas_ano = CaixaPdv.objects.filter(
        created_at__year=ano
    ).aggregate(Sum('total'))['total__sum'] or 0.00

    # Ajustar a consulta para produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.filter(
        quantidade_estoque__lte=5,
        controle_estoque=True,
        status='ativado'
    )

    # Preparar os dados para o gráfico
    nomes_produtos = [produto.nome for produto in produtos_estoque_baixo]
    quantidades_estoque = [produto.quantidade_estoque for produto in produtos_estoque_baixo]

    # Vendas por hora do dia
    vendas_por_hora = CaixaPdv.objects.filter(
        created_at__month=mes,
        created_at__year=ano
    ).annotate(hour=ExtractHour('created_at')).values('hour').annotate(count=Count('id')).order_by('hour')

    horas = [0] * 24  # Inicializa a lista de horas com zero
    for venda in vendas_por_hora:
        horas[venda['hour']] = venda['count']

    return render(request, 'index.html', {
        'pedidos_finalizados': pedidos_finalizados,
        'total_vendas_mes': total_vendas_mes,
        'total_produtos': total_produtos,
        'total_vendas_ano': total_vendas_ano,
        'meses': meses,
        'anos': anos,
        'ano': ano,
        'mes': mes,
        'nomes_produtos': nomes_produtos,
        'quantidades_estoque': quantidades_estoque,
        'horas': horas,
    })