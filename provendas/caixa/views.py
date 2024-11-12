# caixa/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from clientes.models import Cliente
from estoque.models import Produto, CategoriaProduto
from .models import CaixaPdv, ProdutoCaixaPdv
from empresas.models import Empresa 
from configuracoes.models import Configuracao
import json


def gerar_cupom_fiscal(request, pedido_id):
    # Busca o pedido (CaixaPdv) pelo ID
    pedido = get_object_or_404(CaixaPdv, id=pedido_id)
    
    # Busca todos os produtos associados ao pedido
    produtos = ProdutoCaixaPdv.objects.filter(caixa_pdv=pedido)
    
    # Busca o cliente, caso exista
    cliente = pedido.cliente
    
    # Busca os dados da empresa para o cabeçalho
    empresa = Empresa.objects.first()  # ou o método que você usar para pegar os dados da empresa

    # Calcula o total com o desconto
    total_com_desconto = pedido.total - pedido.desconto

    # Passa os dados necessários para o template, incluindo o total com desconto
    context = {
        'sale': pedido,
        'produtos': produtos,
        'cliente': cliente,
        'empresa': empresa,
        'total_com_desconto': total_com_desconto,  # Adiciona o total com desconto ao contexto
    }
    
    # Renderiza o template de cupom fiscal
    return render(request, 'caixa/cupom_fiscal.html', context)


def finalizar_venda(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            venda_id = data.get('venda_id')
            numero_pedido = data.get('numero_pedido')
            vendedor_id = data.get('vendedor_id')
            cliente_id = data.get('cliente_id')
            desconto = float(data.get('desconto', 0))
            total = float(data.get('total', '0'))
            status = data.get('status', 'Em aberto')
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
                    status=status
                )

            # Salva os produtos quando a venda está em aberto, sem ajuste de estoque
            if status == "Em aberto":
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
                return JsonResponse({'success': True, 'message': 'Venda salva com sucesso!'})

            # Caso contrário, se for "Finalizado", processa como finalização de venda
            else:
                ProdutoCaixaPdv.objects.filter(caixa_pdv=caixa_pdv).delete()
                for produto_data in produtos:
                    produto = Produto.objects.filter(id=produto_data.get('produto_id')).first()
                    
                    if produto:
                        quantidade = produto_data['quantidade']

                        # Permite finalizar a venda para produtos com quantidade_estoque zero
                        if produto.quantidade_estoque == 0:
                            ProdutoCaixaPdv.objects.create(
                                caixa_pdv=caixa_pdv,
                                produto=produto,
                                quantidade=quantidade,
                                preco_unitario=produto_data['preco_unitario'],
                                total=quantidade * produto_data['preco_unitario']
                            )
                        elif produto.quantidade_estoque >= quantidade:
                            # Ajusta o estoque para produtos com quantidade suficiente
                            produto.quantidade_estoque -= quantidade
                            produto.save()
                            ProdutoCaixaPdv.objects.create(
                                caixa_pdv=caixa_pdv,
                                produto=produto,
                                quantidade=quantidade,
                                preco_unitario=produto_data['preco_unitario'],
                                total=quantidade * produto_data['preco_unitario']
                            )
                        else:
                            return JsonResponse({'success': False, 'message': 'Estoque insuficiente para um dos produtos.'}, status=400)

                # Atualiza o status do pedido como "Finalizado"
                caixa_pdv.status = 'Finalizado'
                caixa_pdv.save()

                return JsonResponse({'success': True, 'message': 'Venda finalizada com sucesso!'})

        except Exception as e:
            print("Erro ao processar a venda:", e)
            return JsonResponse({'success': False, 'message': f'Erro ao salvar a venda: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)
    
def search_client(request):
    term = request.GET.get('q', '')
    clientes = Cliente.objects.filter(nome__icontains=term)[:10]  # Limite de 10 resultados
    results = [{"id": cliente.id, "nome": cliente.nome} for cliente in clientes]
    return JsonResponse(results, safe=False)

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
            'precoCusto': product.preco_de_cursto,
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

# caixa/views.py
def listar_caixa(request):
    # Busca todos os pedidos do CaixaPdv
    
    pedidos = CaixaPdv.objects.all()  # Todos os pedidos
    clientes = Cliente.objects.all()  # Todos os clientes
    produtos = Produto.objects.all()   # Todos os produtos
    categorias = CategoriaProduto.objects.all()  # Todas as categorias de produtos

    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    cliente_padrao = configuracao.cliente_padrao if configuracao else None

    return render(request, 'caixa/listar_caixa.html', {
        'pedidos': pedidos, 
        'clientes': clientes, 
        'produtos': produtos,
        'categorias': categorias,
        'cliente_padrao': cliente_padrao,
    })

def abrir_caixa_pdv(request):
    # Busca todos os pedidos do CaixaPdv
    pedidos = CaixaPdv.objects.all()  # Todos os pedidos
    clientes = Cliente.objects.all()  # Todos os clientes
    produtos = Produto.objects.all()   # Todos os produtos
    categorias = CategoriaProduto.objects.all()  # Todas as categorias de produtos

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
    })

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
