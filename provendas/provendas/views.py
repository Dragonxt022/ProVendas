from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from django.db.models import Sum, Count
from datetime import datetime
from django.utils.timezone import now

def login_view(request):
    # Verifica se o usuário já está autenticado
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redireciona para o dashboard

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redireciona para a página inicial após o login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')


@login_required

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

    # 1. Quantidade de Pedidos Finalizados
    pedidos_finalizados = CaixaPdv.objects.filter(status='Finalizado').count()

    # 2. Valor Total de Vendas no Mês Atual
    total_vendas_mes = CaixaPdv.objects.filter(
        created_at__month=mes,
        created_at__year=ano
    ).aggregate(Sum('total'))['total__sum'] or 0.00

    # 3. Número de Produtos Cadastrados
    total_produtos = ProdutoCaixaPdv.objects.count()

    # 4. Valor Total de Vendas no Ano Atual
    total_vendas_ano = CaixaPdv.objects.filter(
        created_at__year=ano
    ).aggregate(Sum('total'))['total__sum'] or 0.00

    # Passando os dados para o template
    return render(request, 'index.html', {
        'pedidos_finalizados': pedidos_finalizados,
        'total_vendas_mes': total_vendas_mes,
        'total_produtos': total_produtos,
        'total_vendas_ano': total_vendas_ano,
        'meses': meses,
        'anos': anos,  # Passando a lista de anos para o template
        'ano': ano,  # Passando o ano para o template
        'mes': mes,  # Passando o mês para o template
    })