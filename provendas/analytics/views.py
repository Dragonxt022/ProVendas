from django.shortcuts import render
from caixa.models import CaixaPdv, ProdutoCaixaPdv
from estoque.models import Produto
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractHour
from django.utils.timezone import now
import calendar
from datetime import datetime

def filtro_relatorio_produtos(request):
    # Obtendo os parâmetros de filtro da query string
    ano = request.GET.get('ano')
    mes = request.GET.get('mes')
    dia = request.GET.get('dia')
    tipo = request.GET.get('tipo', 'vendas')  # Tipo de relatório (estoque ou vendas)

    # Lista de anos desde 2020 até o ano atual
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    dia_atual = datetime.now().day
    anos = list(range(2020, ano_atual + 1))

    # Lista de meses do ano
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    # Base queryset para produtos ativos e que controlam o estoque
    produtos = Produto.objects.filter(status='ativado', controle_estoque=True)

    # Se o ano não for passado, usar o ano atual
    if not ano:
        ano = str(ano_atual)
        ano_int = ano_atual  # Define ano_int para o ano atual
    else:
        try:
            ano_int = int(ano)
            produtos = produtos.filter(created_at__year=ano_int)
        except ValueError:
            pass  # Caso o ano não seja válido, não aplica o filtro

    # Se o mês não for passado, usar o mês atual
    if not mes:
        mes = str(mes_atual)
        mes_int = mes_atual  # Define mes_int para o mês atual
    else:
        try:
            mes_int = int(mes)
            produtos = produtos.filter(created_at__month=mes_int)
        except ValueError:
            pass  # Caso o mês não seja válido, não aplica o filtro

    # Se o dia for passado, filtrar por dia específico
    if dia:
        try:
            # Ajuste aqui para filtrar por data completa: ano, mês e dia
            dia_int = datetime.strptime(dia, "%Y-%m-%d").day  # Converte a data para um objeto datetime
            # Filtro utilizando o dia exato com ano e mês
            produtos = produtos.filter(created_at__year=ano_int, created_at__month=mes_int, created_at__day=dia_int)
        except ValueError:
            pass  # Caso o dia não seja válido, não aplica o filtro

    # Variáveis para armazenar os totais
    total_vendas = 0
    total_bruto = 0
    valor_liquido_total = 0

    # Definir os dados de produtos dependendo do tipo
    if tipo == 'estoque':
        # Filtro para estoque: buscando produtos com quantidade em estoque
        produtos_dados = produtos.values('nome', 'quantidade_estoque')
        colunas = ['Nome do Produto', 'Quantidade em Estoque']  # Colunas para estoque
    elif tipo == 'vendas':
        # Filtro para vendas: buscando dados de vendas com soma de quantidade total vendida
        produtos_dados = ProdutoCaixaPdv.objects.filter(produto__in=produtos).values(
            'produto__nome',
            'produto__preco_de_custo',
            'produto__preco_de_venda'  # Incluindo o preço unitário
        ).annotate(
            quantidade_total=Sum('quantidade'),
            valor_total=Sum(F('quantidade') * F('preco_unitario')),
            valor_bruto=Sum(F('quantidade') * (F('produto__preco_de_venda') - F('produto__preco_de_custo')))
        ).order_by('-quantidade_total')

        # Calculando os totais
        total_vendas = produtos_dados.aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or 0
        total_bruto = produtos_dados.aggregate(total_bruto=Sum('valor_bruto'))['total_bruto'] or 0
        valor_liquido_total = total_bruto  # O total líquido é basicamente o valor bruto menos custos

        colunas = [
            'Nome do Produto',
            'Qty Vendida',
            'Preço de Custo',
            'Preço de Venda',
            'Total Bruto',
            'Total Liquido',
        ]  # Colunas para vendas

    return render(request, 'analytics/analytics_avancado.html', {
        'produtos_dados': produtos_dados,
        'ano': ano,
        'mes': mes,
        'dia': dia,
        'anos': anos,
        'meses': meses,
        'tipo': tipo,  # Passando o tipo para o template
        'colunas': colunas,  # Passando as colunas dinâmicas
        'valor_liquido_total': valor_liquido_total,  # Passando o total líquido para o template
        'total_vendas': total_vendas,  # Passando o total das vendas
        'total_bruto': total_bruto,  # Passando o total bruto
    })




def analytics_desboard(request):
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


