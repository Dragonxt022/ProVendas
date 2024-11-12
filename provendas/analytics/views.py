from django.shortcuts import render
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from django.db.models import Sum, Count
from django.utils.timezone import now
import calendar

def analytics_desboard(request):
    # Exemplo de dados para o painel de controle
    pedidos_finalizados = CaixaPdv.objects.filter(status='Finalizado').count()
    total_vendas_mes = CaixaPdv.objects.filter(
        created_at__month=now().month
    ).aggregate(Sum('total'))['total__sum'] or 0
    total_produtos = ProdutoCaixaPdv.objects.count()

    # Vendas por mês (Usando CaixaPdv)
    vendas_por_mes = CaixaPdv.objects.filter(
        created_at__year=now().year
    ).values('created_at__month').annotate(total_vendas=Sum('total')).order_by('created_at__month')

    # Organizando os dados para enviar ao gráfico de vendas por mês
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    vendas_mes = [0] * 12  # Inicializa a lista de vendas por mês com zero
    for venda in vendas_por_mes:
        vendas_mes[venda['created_at__month'] - 1] = float(venda['total_vendas'] or 0)

    # Contagem das formas de pagamento mais usadas
    formas_pagamento = CaixaPdv.objects.values('payment_method').annotate(count=Count('payment_method')).order_by('-count')

    # Extrair dados para o gráfico de formas de pagamento
    payment_methods = [fp['payment_method'] for fp in formas_pagamento]
    payment_counts = [fp['count'] for fp in formas_pagamento]

    return render(request, 'analytics/analytics_desboard.html', {
        'pedidos_finalizados': pedidos_finalizados,
        'total_vendas_mes': total_vendas_mes,
        'total_produtos': total_produtos,
        'vendas_mes': vendas_mes,
        'meses': meses,
        'payment_methods': payment_methods,
        'payment_counts': payment_counts,
    })
