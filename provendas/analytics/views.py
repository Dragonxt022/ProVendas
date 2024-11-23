from django.shortcuts import render
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from estoque.models import Produto
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractHour
from django.utils.timezone import now
from datetime import datetime

def filtro_relatorio_produtos(request):
    # Obtendo os parâmetros de filtro da query string
    ano = request.GET.get('ano')
    mes = request.GET.get('mes')
    dia = request.GET.get('dia')
    controle_estoque = request.GET.get('controle_estoque')

    # Obter o ano, mês e dia atuais
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    dia_atual = datetime.now().day

    # Função para garantir que os parâmetros sejam inteiros válidos ou retornar o valor atual
    def get_valid_int_param(param, default_value):
        try:
            return int(param) if param else default_value
        except ValueError:
            return default_value

    # Processar os parâmetros de ano, mês e dia
    ano_int = get_valid_int_param(ano, ano_atual)
    mes_int = get_valid_int_param(mes, mes_atual)
    dia_int = get_valid_int_param(dia, dia_atual)

    # Definir os filtros iniciais
    filtros = {'status': 'ativado'}

    if dia:
        # Se apenas o dia foi informado, usar ano e mês padrão
        filtros['created_at__year'] = ano_int
        filtros['created_at__month'] = mes_int
        filtros['created_at__day'] = dia_int
    else:
        if ano:
            filtros['created_at__year'] = ano_int
        if mes:
            filtros['created_at__month'] = mes_int

    # Filtro para controle_estoque
    if controle_estoque == 'True':
        filtros['controle_estoque'] = True
    elif controle_estoque == 'False':
        filtros['controle_estoque'] = False
    elif controle_estoque == 'ambos':
        # Sem filtro específico, ou seja, inclui os dois casos
        pass

    # Filtrar produtos baseados nos critérios
    produtos = Produto.objects.filter(**filtros)

    # Relatório de vendas
    produtos_dados = ProdutoCaixaPdv.objects.filter(produto__in=produtos).select_related('produto').values(
        'produto__nome',
        'produto__preco_de_custo',
        'produto__preco_de_venda'
    ).annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum(F('quantidade') * F('preco_unitario')),
        valor_bruto=Sum(F('quantidade') * (F('produto__preco_de_venda') - F('produto__preco_de_custo')))
    ).order_by('-quantidade_total')

    # Calculando os totais
    total_vendas = produtos_dados.aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or 0
    total_bruto = produtos_dados.aggregate(total_bruto=Sum('valor_bruto'))['total_bruto'] or 0
    valor_liquido_total = total_bruto

    # Arredondando para duas casas decimais (se necessário)
    total_vendas = round(total_vendas, 2)
    total_bruto = round(total_bruto, 2)
    valor_liquido_total = round(valor_liquido_total, 2)

    # Preparar colunas para o relatório
    colunas = ['Produto', 'Qty Vendida', 'Preço de Custo', 'Preço de Venda', 'Valor Total', 'Valor Bruto']

    # Preparar dados formatados para o template
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    anos = list(range(2024, ano_atual + 1))
    dias = list(range(1, 32))  # Lista de dias possíveis


    ### Mais relatórios #####

    pedidos_finalizados = CaixaPdv.objects.filter(status='Finalizado').count()
    total_vendas_mes = CaixaPdv.objects.filter(
        created_at__month=mes_int,
        created_at__year=ano_int
    ).aggregate(Sum('total'))['total__sum'] or 0
    total_produtos = ProdutoCaixaPdv.objects.count()

    # Vendas por mês (Usando CaixaPdv)
    vendas_por_mes = CaixaPdv.objects.filter(
        created_at__year=ano_int
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
        created_at__month=mes_int,
        created_at__year=ano_int
    ).annotate(hour=ExtractHour('created_at')).values('hour').annotate(count=Count('id')).order_by('hour')

    horas = [0] * 24  # Inicializa a lista de horas com zero
    for venda in vendas_por_hora:
        horas[venda['hour']] = venda['count']

    # Vendas por dia da semana (Alternativa sem ExtractWeekday)
    vendas = CaixaPdv.objects.filter(created_at__month=mes_int, created_at__year=ano_int)
    dias_semana = [0] * 7  # Inicializa a lista de dias da semana com zero
    for venda in vendas:
        weekday = venda.created_at.weekday()  # Retorna 0 (segunda-feira) a 6 (domingo)
        dias_semana[weekday] += 1

    # Mapeamento dos dias da semana
    dias_da_semana = [
        'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'
    ]

    # Definindo o número máximo de produtos a serem mostrados
    MAX_ITENS = 10

    # Produtos mais vendidos com conversão de Decimal para float
    produtos_mais_vendidos = ProdutoCaixaPdv.objects.values(
        'produto__nome'
    ).annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum(F('quantidade') * F('preco_unitario'))
    ).order_by('-quantidade_total')[:MAX_ITENS]


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


    return render(request, 'analytics/analytics_avancado.html', {
        'produtos_dados': produtos_dados,
        'ano': ano,
        'mes': mes,
        'dia': dia,
        'controle_estoque': controle_estoque,
        'anos': anos,
        'meses': meses,
        'dias': dias,
        'colunas': colunas,  # Colunas dinâmicas
        'valor_liquido_total': valor_liquido_total,
        'total_vendas': total_vendas,
        'total_bruto': total_bruto,
        'ano_formatado': ano_int,
        'mes_formatado': meses[mes_int - 1] if mes else None,
        'dia_formatado': dia_int if dia else None,
        'total_produtos': total_produtos,
        'pedidos_finalizados': pedidos_finalizados,
        'total_vendas_mes': total_vendas_mes,
        'vendas_mes': vendas_mes,
        'payment_methods': payment_methods,
        'payment_counts': payment_counts,
        'vendas_por_hora': horas,
        'dias_da_semana': dias_semana,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'produtos_estoque_baixo': produtos_estoque_baixo,

        'nomes_produtos': nomes_produtos,
        'quantidades_estoque': quantidades_estoque,

        'produtos_nomes': produtos_nomes,
        'produtos_quantidades': produtos_quantidades,
        'produtos_valores': produtos_valores,
    })



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


