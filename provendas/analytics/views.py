from django.shortcuts import render
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from estoque.models import Produto
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractHour
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.http import JsonResponse


def relatorio_vendas(request):
    
    return render(request, "analytics/analytics_avancado.html")

def relatorio_vendas_ajax(request):
    if request.method == "GET":
        # Recuperar os filtros de data da requisição GET
        data_inicio = request.GET.get("data_inicio")
        data_fim = request.GET.get("data_fim")

        # Validar e converter as datas
        try:
            if data_inicio:
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            if data_fim:
                data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"error": "Formato de data inválido"}, status=400)
        
        # Se a data de início e a data de fim forem as mesmas, adicionar 24 horas à data de início
        if data_inicio and data_fim and data_inicio == data_fim:
            data_fim = data_inicio + timedelta(days=1)

        # Filtro base
        filtro = {"status": "Finalizado"}
        if data_inicio:
            filtro["created_at__gte"] = data_inicio
        if data_fim:
            filtro["created_at__lte"] = data_fim

        # Total de vendas por método de pagamento
        vendas_por_metodo_pagamento = list(
            CaixaPdv.objects.filter(**filtro)
            .values("payment_method")
            .annotate(total_vendas=Sum("total"), quantidade=Count("id"))
            .order_by("-total_vendas")
        )

        # Produtos mais vendidos
        produtos_mais_vendidos = list(
            ProdutoCaixaPdv.objects.filter(caixa_pdv__created_at__gte=data_inicio, caixa_pdv__created_at__lte=data_fim)
            .values(produto_nome=F("produto__nome"))
            .annotate(total_vendido=Sum("quantidade"), receita_total=Sum("total"))
            .order_by("-total_vendido")
        )

        # Total geral de vendas e receita
        total_vendas = CaixaPdv.objects.filter(**filtro).aggregate(
            receita_total=Sum("total"), quantidade_total=Sum("subtotal")
        )

        # Dados a serem retornados
        data = {
            "vendas_por_metodo_pagamento": vendas_por_metodo_pagamento,
            "produtos_mais_vendidos": produtos_mais_vendidos,
            "total_vendas": total_vendas,
        }
        return JsonResponse(data, safe=False)
    return JsonResponse({"error": "Método não permitido"}, status=405)




def analytics_desboard(request):
    # Pegando o ano e mês da query string ou usando os valores atuais
    ano = int(request.GET.get('ano', now().year))
    mes = int(request.GET.get('mes', now().month))

    # Gerar lista de anos desde 2024 até o ano atual
    ano_atual = datetime.now().year
    anos = list(range(2024, ano_atual + 1))

    # Lista de meses do ano
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    # Exemplo de dados para o painel de controle
    pedidos_finalizados = CaixaPdv.objects.filter(status='Finalizado').count()
    total_vendas_mes = CaixaPdv.objects.filter(
        created_at__month=mes,
        created_at__year=ano
    ).aggregate(Sum('total'))['total__sum'] or 0
    total_produtos = ProdutoCaixaPdv.objects.count()

    # Vendas por mês (Usando CaixaPdv)
    vendas_por_mes = CaixaPdv.objects.filter(
        created_at__year=ano
    ).values('created_at__month').annotate(total_vendas=Sum('total')).order_by('created_at__month')

    vendas_mes = [0] * 12  # Inicializa a lista de vendas por mês com zero
    for venda in vendas_por_mes:
        vendas_mes[venda['created_at__month'] - 1] = float(venda['total_vendas'] or 0)

    # Contagem das formas de pagamento mais usadas
    formas_pagamento = CaixaPdv.objects.values('payment_method').annotate(count=Count('payment_method')).order_by('-count')

    # Extrair dados para o gráfico de formas de pagamento
    payment_methods = [fp['payment_method'] for fp in formas_pagamento]
    payment_counts = [fp['count'] for fp in formas_pagamento]

    # Vendas por hora do dia
    vendas_por_hora = CaixaPdv.objects.filter(
        created_at__month=mes,
        created_at__year=ano
    ).annotate(hour=ExtractHour('created_at')).values('hour').annotate(count=Count('id')).order_by('hour')

    horas = [0] * 24  # Inicializa a lista de horas com zero
    for venda in vendas_por_hora:
        horas[venda['hour']] = venda['count']

    # Vendas por dia da semana (Alternativa sem ExtractWeekday)
    vendas = CaixaPdv.objects.filter(created_at__month=mes, created_at__year=ano)
    dias_semana = [0] * 7  # Inicializa a lista de dias da semana com zero
    for venda in vendas:
        weekday = venda.created_at.weekday()  # Retorna 0 (segunda-feira) a 6 (domingo)
        dias_semana[weekday] += 1

    # Mapeamento dos dias da semana
    dias_da_semana = [
        'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'
    ]

    # Produtos mais vendidos com conversão de Decimal para float
    produtos_mais_vendidos = ProdutoCaixaPdv.objects.values(
        'produto__nome'
    ).annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum(F('quantidade') * F('preco_unitario'))
    ).order_by('-quantidade_total')


    # Ajustar a consulta para produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.filter(
        quantidade_estoque__lte=5,
        controle_estoque=True,
        status='ativado'
    )

    # Preparar os dados para o gráfico
    nomes_produtos = [produto.nome for produto in produtos_estoque_baixo]
    quantidades_estoque = [produto.quantidade_estoque for produto in produtos_estoque_baixo]


    # Convertendo os valores de Decimal para float
    produtos_nomes = [produto['produto__nome'] for produto in produtos_mais_vendidos]
    produtos_quantidades = [float(produto['quantidade_total']) for produto in produtos_mais_vendidos]
    produtos_valores = [float(produto['valor_total']) for produto in produtos_mais_vendidos]

    return render(request, 'analytics/analytics_desboard.html', {
        'pedidos_finalizados': pedidos_finalizados,
        'total_vendas_mes': total_vendas_mes,
        'total_produtos': total_produtos,
        'vendas_mes': vendas_mes,
        'meses': meses,
        'anos': anos,  # Passando a lista de anos para o template
        'payment_methods': payment_methods,
        'payment_counts': payment_counts,
        'horas': horas,  # Dados das vendas por hora
        'dias_semana': dias_semana,  # Dados dos dias da semana
        'dias_da_semana': dias_da_semana,  # Nomes dos dias da semana
        'produtos_nomes': produtos_nomes,  # Nomes dos produtos mais vendidos
        'produtos_quantidades': produtos_quantidades,  # Quantidades dos produtos mais vendidos
        'produtos_valores': produtos_valores,  # Valores totais dos produtos mais vendidos
        'ano': ano,  # Passando o ano para o template
        'mes': mes,  # Passando o mês para o template
        'nomes_produtos': nomes_produtos,
        'quantidades_estoque': quantidades_estoque,
    })


