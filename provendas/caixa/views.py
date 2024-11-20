# caixa/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from clientes.models import Cliente
from estoque.models import Produto, CategoriaProduto
from .models import CaixaPdv, ProdutoCaixaPdv, Caixa
from empresas.models import Empresa 
from configuracoes.models import Configuracao
import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q 
import locale
import logging
logger = logging.getLogger(__name__)

#  Abre o caixa
def abrir_caixa_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Verificar se já existe um caixa aberto
        caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()
        if caixa_aberto:
            return JsonResponse({'success': False, 'message': "Você já tem um caixa aberto."})

        saldo_inicial = float(request.POST.get('saldo_inicial', 0.00))
        novo_caixa = Caixa.objects.create(usuario=request.user, saldo_inicial=saldo_inicial)
        return JsonResponse({'success': True, 'message': "Caixa aberto com sucesso."})
    return JsonResponse({'success': False, 'message': "Requisição inválida."})

# Fecha o caixa
def fechar_caixa_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Carregar o corpo da requisição JSON
            data = json.loads(request.body)
            saldo_final = data.get('saldo_final')

            # Log para verificar o valor recebido
            logger.debug(f"Dados recebidos: {data}")
            logger.debug(f"Saldo final: {saldo_final}")

            # Verificar se o saldo final foi fornecido
            if not saldo_final:
                logger.error("Saldo final não foi fornecido")
                return JsonResponse({'success': False, 'message': "Saldo final não fornecido."})

            saldo_final = float(saldo_final)  # Garantir que é um número float

            # Buscar o caixa aberto para o usuário
            caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()

            if not caixa_aberto:
                logger.error(f"Nenhum caixa aberto encontrado para o usuário {request.user.id}")
                return JsonResponse({'success': False, 'message': "Não há caixa aberto para fechar."})

            # Atualizar o saldo final e status do caixa
            caixa_aberto.saldo_final = saldo_final
            caixa_aberto.status = 'Fechado'
            caixa_aberto.fechado_em = timezone.now()  # Registrar a data de fechamento
            caixa_aberto.save()

            logger.info(f"Caixa {caixa_aberto.id} fechado com sucesso")

            return JsonResponse({'success': True, 'message': "Caixa fechado com sucesso."})
        except Exception as e:
            logger.error(f"Erro ao tentar fechar o caixa: {str(e)}")
            return JsonResponse({'success': False, 'message': f"Erro ao fechar o caixa: {str(e)}"})
    
    logger.error("Requisição inválida: método não POST ou não AJAX")
    return JsonResponse({'success': False, 'message': "Requisição inválida."})

# Verifica se tem algum caixa aberto
def verificar_caixa_aberto(request):
    caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').exists()

    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    abrir_caixa_automatico = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False

    return JsonResponse({
        'caixa_aberto': caixa_aberto,
        'abrir_caixa_automatico': abrir_caixa_automatico
    })

#  FInaliza a venda via Ajax
def salvar_produtos_na_venda(caixa_pdv, produtos):
    try:
        # Limpa os produtos anteriores associados à venda
        ProdutoCaixaPdv.objects.filter(caixa_pdv=caixa_pdv).delete()
        
        for produto_data in produtos:
            produto = Produto.objects.filter(id=produto_data.get('produto_id')).first()
            if produto:
                ProdutoCaixaPdv.objects.create(
                    caixa_pdv=caixa_pdv,
                    produto=produto,
                    quantidade=produto_data.get('quantidade'),
                    preco_unitario=produto_data.get('preco_unitario'),
                    total=produto_data['quantidade'] * produto_data['preco_unitario']
                )
            else:
                print(f"Produto não encontrado: ID {produto_data.get('produto_id')}")
    except Exception as e:
        print(f"Erro ao salvar produtos: {e}")

def finalizar_venda(request):
    if request.method == 'POST':  # Certifique-se de que a requisição é POST
        try:
            configuracao = Configuracao.objects.first()
            gerenciar_abertura_fechamento_caixa = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False

            data = json.loads(request.body)

            venda_id = data.get('venda_id')
            numero_pedido = data.get('numero_pedido')
            vendedor_id = data.get('vendedor_id')
            cliente_id = data.get('cliente_id')
            desconto = float(data.get('desconto', 0))
            total = float(data.get('total', '0'))
            status = data.get('status', 'Em aberto')
            payment_method = data.get('payment_method')
            produtos = data.get('produtos', [])

            # Verifica se a venda já existe para atualizar, caso contrário, cria uma nova
            if venda_id:
                caixa_pdv = CaixaPdv.objects.filter(id=venda_id).first()
                if not caixa_pdv:
                    return JsonResponse({'success': False, 'message': 'Venda não encontrada.'}, status=404)
            else:
                # Criando nova venda
                cliente = Cliente.objects.filter(id=cliente_id).first()
                vendedor = User.objects.filter(id=vendedor_id).first()

                if not cliente:
                    return JsonResponse({'success': False, 'message': 'Cliente não encontrado.'}, status=404)
                if not vendedor:
                    return JsonResponse({'success': False, 'message': 'Vendedor não encontrado.'}, status=404)

                caixa_pdv = CaixaPdv.objects.create(
                    numero_pedido=numero_pedido,
                    vendedor=vendedor,
                    cliente=cliente,
                    desconto=desconto,
                    total=total,
                    status=status,
                    payment_method=payment_method
                )

                # Se a venda não estiver finalizada, não associa ao caixa
                if status != 'Finalizado' and gerenciar_abertura_fechamento_caixa:
                    return JsonResponse({'success': True, 'message': 'Venda salva sem associação ao caixa.'})

            # Salva os produtos quando a venda está em aberto, sem ajuste de estoque
            if status == "Em aberto":
                salvar_produtos_na_venda(caixa_pdv, produtos)

            # Caso contrário, se for "Finalizado", processa como finalização de venda
            else:
                salvar_produtos_na_venda(caixa_pdv, produtos)

                # Ajuste de estoque e finalização de venda
                for produto_data in produtos:
                    produto = Produto.objects.filter(id=produto_data.get('produto_id')).first()

                    if produto:
                        quantidade = produto_data['quantidade']

                        # Verifica se o produto é gerenciável (controle_estoque é True)
                        if produto.controle_estoque:
                            # Permite a venda mesmo com estoque 0 e ajusta o estoque, permitindo números negativos
                            produto.quantidade_estoque -= quantidade  # Subtrai a quantidade da venda
                            produto.save()
                        # Caso o produto não seja gerenciável, não altera o estoque e apenas realiza a venda
                        # Nenhuma ação é necessária aqui, o estoque não será alterado.

                # Se o gerenciamento de caixa estiver ativado, associa a venda ao caixa
                if gerenciar_abertura_fechamento_caixa:
                    caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()
                    if not caixa_aberto:
                        return JsonResponse({'success': False, 'message': 'Não há caixa aberto para associar a venda.'}, status=400)

                    caixa_pdv.caixa = caixa_aberto
                    caixa_pdv.status = 'Finalizado'
                    caixa_pdv.save()

                return JsonResponse({'success': True, 'message': 'Venda finalizada com sucesso!'})

            return JsonResponse({'success': True, 'message': 'Venda finalizada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao salvar a venda: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)


# Gera o Cupom de maneira normal
def gerar_cupom_fiscal(request, pedido_id):
    pedido = get_object_or_404(CaixaPdv, id=pedido_id)
    
    # Busca todos os produtos associados ao pedido
    produtos = ProdutoCaixaPdv.objects.filter(caixa_pdv=pedido)
    
    # Busca o cliente, caso exista
    cliente = pedido.cliente
    
    # Busca os dados da empresa para o cabeçalho
    empresa = Empresa.objects.first()  # ou o método que você usar para pegar os dados da empresa

    # Calcula o subtotal (total + desconto)
    subtotal = pedido.total + pedido.desconto

    # Calcula o total com o desconto (total após o desconto)
    total_com_desconto = pedido.total

    # Passa os dados necessários para o template, incluindo o subtotal, desconto e total com desconto
    context = {
        'sale': pedido,
        'produtos': produtos,
        'cliente': cliente,
        'empresa': empresa,
        'subtotal': subtotal,  # Subtotal (total + desconto)
        'desconto': pedido.desconto,  # Valor do desconto
        'total_com_desconto': total_com_desconto,  # Total após o desconto
    }
    
    # Renderiza o template de cupom fiscal
    return render(request, 'caixa/cupom_fiscal.html', context)

# Busca os clientes cadastrados via AJAX   
def search_client(request):
    term = request.GET.get('q', '')
    clientes = Cliente.objects.filter(nome__icontains=term)[:10]  # Limite de 10 resultados
    results = [{"id": cliente.id, "nome": cliente.nome} for cliente in clientes]
    return JsonResponse(results, safe=False)

# Alimenta a modal de produtos via AJX
def search_products(request):
    if request.method == "GET":
        query = request.GET.get('q', '')  # Termo de busca opcional
        category_id = request.GET.get('category_id', None)  # ID da categoria opcional

        # Busca todos os produtos com status ativado e suas categorias
        products = Produto.objects.filter(status='ativado').select_related('categoria')

        # Filtra produtos com base na busca
        if query:
            products = products.filter(nome__icontains=query)

        # Filtra produtos com base na categoria se um ID de categoria for fornecido
        if category_id:
            products = products.filter(categoria_id=category_id)

        # Prepara os dados para enviar ao front-end
        results = [{
            'id': product.id,
            'nome': product.nome,
            'codigoBarras': product.codigo_barras,
            'preco': product.preco_de_venda,
            'precoCusto': product.preco_de_custo,
            'file': product.file.url if product.file else None,
            'categoria': {
                'id': product.categoria.id,
                'file': product.categoria.file.url if product.categoria.file else None,
                'nome': product.categoria.nome
            } if product.categoria else None
        } for product in products]

        # Busca todas as categorias
        categories = [{
            'id': cat.id,
            'file': cat.file.url if cat.file else None,
            'nome': cat.nome
        } for cat in CategoriaProduto.objects.all()]

        return JsonResponse({'products': results, 'categories': categories})

#Alimenta a lista de Vendas realizadas
def listar_caixa(request):
    # Busca todos os pedidos do CaixaPdv
    pedidos = CaixaPdv.objects.all()  # Todos os pedidos
    clientes = Cliente.objects.all()  # Todos os clientes
    produtos = Produto.objects.all()   # Todos os produtos
    categorias = CategoriaProduto.objects.all()  # Todas as categorias de produtos

    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    cliente_padrao = configuracao.cliente_padrao if configuracao else None
    modoLeitorCodigoDeBarra = configuracao.modoLeitorCodigoDeBarra if configuracao else False
    gerenciar_abertura_fechamento_caixa = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False

    # Busca o caixa aberto para o usuário atual
    caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()
    caixa_esta_aberto = caixa_aberto is not None

    return render(request, 'caixa/listar_caixa.html', {
        'pedidos': pedidos, 
        'clientes': clientes, 
        'produtos': produtos,
        'categorias': categorias,
        'cliente_padrao': cliente_padrao,
        'modoLeitorCodigoDeBarra': modoLeitorCodigoDeBarra, 
        'gerenciar_abertura_fechamento_caixa': gerenciar_abertura_fechamento_caixa,
        'caixa_esta_aberto': caixa_esta_aberto,
    })

#  Alimenta a lista de Vendas realizadas via Ajax
def listar_pedidos_ajax(request):
    # Recebe os parâmetros de filtro da requisição
    search_term = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    vendedor_filter = request.GET.get('vendedor', '')
    cliente_filter = request.GET.get('cliente', '')

    # Consulta base dos pedidos
    pedidos_list = CaixaPdv.objects.all().order_by('-id')  # Ordenar por ID (decrescente)

    # Aplicar filtros
    if search_term:
        pedidos_list = pedidos_list.filter(
            Q(numero_pedido__icontains=search_term) |
            Q(vendedor__username__icontains=search_term) |
            Q(cliente__nome__icontains=search_term) |
            Q(total__icontains=search_term)  # Pesquisa pelo valor total
        )

    if status_filter:
        pedidos_list = pedidos_list.filter(status__icontains=status_filter)

    if vendedor_filter:
        pedidos_list = pedidos_list.filter(vendedor__username__icontains=vendedor_filter)

    if cliente_filter:
        pedidos_list = pedidos_list.filter(cliente__nome__icontains=cliente_filter)

    # Paginação
    paginator = Paginator(pedidos_list, 10)  # 3 pedidos por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    pedidos_data = []
    for pedido in page_obj:
        # Converte 'created_at' para o horário local
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        data_local = timezone.localtime(pedido.created_at)

        pedidos_data.append({
            'id': pedido.id,
            'numero_pedido': pedido.numero_pedido,
            'data': data_local.strftime('%d de %B de %Y, %H:%M'),
            'vendedor': pedido.vendedor.username,
            'cliente': pedido.cliente.nome,
            'total': pedido.total,
            'status': pedido.status
        })

    # Retornar os dados filtrados e informações de paginação
    return JsonResponse({
        'pedidos': pedidos_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

# Gera um cupom não fiscal via Ajax
def cupom_fiscal_ajax(request, pedido_id):
    try:
        # Busca o pedido específico
        pedido = CaixaPdv.objects.get(id=pedido_id)
        
        # Busca os produtos vendidos no pedido
        produtos = ProdutoCaixaPdv.objects.filter(caixa_pdv=pedido)
        
        # Cria uma lista de produtos com os detalhes
        produtos_data = []
        for produto in produtos:
            produtos_data.append({
                'quantidade': produto.quantidade,
                'produto': {
                    'nome': produto.produto.nome,
                    'codigo_barras': produto.produto.codigo_barras
                },
                'preco_unitario': str(produto.preco_unitario),
            })
        
        # Retorna os dados em formato JSON
        return JsonResponse({
            'numero_pedido': pedido.numero_pedido,
            'cliente': pedido.cliente.nome if pedido.cliente else 'Não especificado',
            'total': str(pedido.total),
            'status': pedido.status,
            'produtos': produtos_data
        })
    except CaixaPdv.DoesNotExist:
        return JsonResponse({'error': 'Pedido não encontrado'}, status=404)

#  Abre Caixa PDV
def abrir_caixa_pdv(request):
    # Busca todos os pedidos do CaixaPdv
    pedidos = CaixaPdv.objects.all()  # Todos os pedidos
    clientes = Cliente.objects.all()  # Todos os clientes
    produtos = Produto.objects.all()   # Todos os produtos
    categorias = CategoriaProduto.objects.all()  # Todas as categorias de produtos
    
    # Busca o caixa aberto para o usuário atual
    caixa_aberto = Caixa.objects.filter(usuario=request.user, status='Aberto').first()


    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    modoLeitorCodigoDeBarra = configuracao.modoLeitorCodigoDeBarra if configuracao else False
    gerenciar_abertura_fechamento_caixa = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False

    # Define se o caixa está aberto e passa mais informações se necessário
    caixa_esta_aberto = caixa_aberto is not None
    status_caixa = caixa_aberto.status if caixa_aberto else 'N/D'


    pedido = None
    pedido_id = request.GET.get('id')  # Obtém o ID do pedido da URL

    if pedido_id:
        pedido = get_object_or_404(CaixaPdv, id=pedido_id)  # Busca o pedido pelo ID

    # Busca os produtos relacionados ao pedido, se existir
    produtos_do_pedido = ProdutoCaixaPdv.objects.filter(caixa_pdv=pedido) if pedido else []

    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    cliente_padrao = configuracao.cliente_padrao if configuracao else None

    return render(request, 'caixa/caixa_pdv.html', {
        'pedidos': pedidos, 
        'clientes': clientes, 
        'produtos': produtos,
        'categorias': categorias,
        'pedido': pedido,  # Passa o pedido encontrado para o template
        'produtos_do_pedido': produtos_do_pedido,  # Passa os produtos do pedido para o template
        'cliente_padrao': cliente_padrao,  # Passa o cliente padrão para o template
        'caixa_esta_aberto': caixa_esta_aberto,
        'status_caixa': status_caixa,
        'modoLeitorCodigoDeBarra': modoLeitorCodigoDeBarra, 
        'gerenciar_abertura_fechamento_caixa': gerenciar_abertura_fechamento_caixa,
    })

#  Veja os detalhes de cada vejda
def get_venda_details(request, id):
    # Busca o pedido pelo ID
    pedido = get_object_or_404(CaixaPdv, id=id)

    # Busca os produtos relacionados a esse pedido
    produtos = ProdutoCaixaPdv.objects.filter(caixa_pdv=pedido)

    # Estruturar os dados que serão retornados
    data = {
        'id': pedido.id,
        'numero_pedido': pedido.numero_pedido,
        'vendedor': {
            'id': pedido.vendedor.id,
            'nome': pedido.vendedor.username,  # Ajuste conforme necessário
        },
        'status': pedido.status,
        'desconto': pedido.desconto,
        'total': pedido.total,
        'produtos': [{
            'produto': {
                'id': produto.produto.id,
                'nome': produto.produto.nome,
                'codigoBarras': produto.produto.codigo_barras or "",  # Valor padrão
                'file': produto.produto.file.url if produto.produto.file else None,  # Imagem do produto, se houver
                'categoria': {
                    'nome': produto.produto.categoria.nome if produto.produto.categoria else None,
                    'file': produto.produto.categoria.file.url if produto.produto.categoria and produto.produto.categoria.file else None  # Imagem da categoria, se houver
                } if produto.produto.categoria else None,
            },
            'quantidade': produto.quantidade,  # Campo quantidade
            'preco_unitario': produto.preco_unitario,  # Preço unitário para log
            'total': produto.total,  # Total para log
        } for produto in produtos]
    }

    # Log dos valores para verificar quantidade e outros detalhes antes da conversão
    for produto in data['produtos']:
        print(
            f"Produto ID: {produto['produto']['id']}, Nome: {produto['produto']['nome']}, "
            f"Quantidade: {produto['quantidade']}, Preço Unitário: {produto['preco_unitario']}, Total: {produto['total']}"
        )

    return JsonResponse(data)

# Exluir vendas
def excluir_venda(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            venda_id = data.get('venda_id')

            # Recupera a venda
            caixa_pdv = CaixaPdv.objects.filter(id=venda_id).first()
            if not caixa_pdv:
                return JsonResponse({'success': False, 'message': 'Venda não encontrada.'}, status=404)

            # Recupera os produtos da venda
            produtos = ProdutoCaixaPdv.objects.filter(caixa_pdv=caixa_pdv)

            # Adiciona os produtos de volta ao estoque apenas se controle de estoque estiver ativado
            for produto in produtos:
                produto_obj = Produto.objects.filter(id=produto.produto.id).first()
                if produto_obj:
                    # Verifica se o produto tem controle de estoque
                    if produto_obj.controle_estoque == 1:  # Ou True, dependendo da implementação
                        produto_obj.quantidade_estoque += produto.quantidade
                        produto_obj.save()

            # Exclui a venda
            caixa_pdv.delete()

            return JsonResponse({'success': True, 'message': 'Venda excluída com sucesso e produtos devolvidos ao estoque.'})

        except Exception as e:
            print("Erro ao excluir a venda:", e)
            return JsonResponse({'success': False, 'message': f'Erro ao excluir a venda: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)
