# comanda/views.py

# Imports padrão do Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
import json
import logging
import random

# Imports dos modelos e forms do seu projeto
from caixa.models import CaixaPdv, ProdutoCaixaPdv, Caixa
from .models import Mesa, Comanda, ProdutoComanda
from .forms import MesaForm
from clientes.models import Cliente
from empresas.models import Empresa
from configuracoes.models import Configuracao
from estoque.models import Produto, CategoriaProduto


logger = logging.getLogger(__name__)

# Gera cupon fiscal da parte de comanda
def gerar_cupom_fiscal_comanda(request, comanda_id):
    # Busca a comanda pelo ID
    comanda = get_object_or_404(Comanda, id=comanda_id)
    
    # Busca todos os produtos associados à comanda
    produtos = ProdutoComanda.objects.filter(comanda=comanda)
    
    # Busca o cliente, caso exista
    cliente = comanda.cliente
    
    # Busca os dados da empresa para o cabeçalho
    empresa = Empresa.objects.first()  # ou o método que você usar para pegar os dados da empresa
    
    # Passa os dados necessários para o template
    context = {
        'comanda': comanda,
        'produtos': produtos,
        'cliente': cliente,
        'empresa': empresa,
    }
    
    # Renderiza o template de cupom fiscal
    return render(request, 'comanda/cupom_fiscal.html', context)

# def fechar_comanda(request, mesa_id):
#     if request.method == 'POST':
#         try:
#             # Capturar os dados da requisição
#             data = json.loads(request.body)
#             numero_pedido = data.get('numero_pedido')
#             vendedor_id = data.get('vendedor_id')
#             cliente_id = data.get('cliente_id')
#             desconto = data.get('desconto', 0.0)
#             total = data.get('total')
#             payment_method = data.get('payment_method')
#             produtos = data.get('produtos', [])

#             # Buscar a mesa e a comanda aberta associada
#             mesa = get_object_or_404(Mesa, id=mesa_id)
#             comanda = get_object_or_404(Comanda, mesa=mesa, status='aberta')

#             # Verifica se a comanda já foi fechada e converte para uma venda
#             cliente = Cliente.objects.filter(id=cliente_id).first()
#             vendedor = User.objects.filter(id=vendedor_id).first()

#             if not cliente or not vendedor:
#                 return JsonResponse({'success': False, 'message': 'Cliente ou Vendedor não encontrado.'}, status=404)

#             # Criando a venda (CaixaPdv)
#             caixa_pdv = CaixaPdv.objects.create(
#                 numero_pedido=numero_pedido,
#                 vendedor=vendedor,
#                 cliente=cliente,
#                 desconto=desconto,
#                 total=total,
#                 status="Finalizado",  # Marcar como finalizado direto ao fechar a comanda
#                 payment_method=payment_method
#             )

#             # Processar os produtos e salvar no CaixaPdv
#             for produto_data in produtos:
#                 produto = Produto.objects.filter(id=produto_data.get('produto_id')).first()

#                 if produto:
#                     quantidade = produto_data['quantidade']

#                     # Verificar se o controle de estoque está ativado
#                     if produto.controle_estoque:
#                         if produto.quantidade_estoque >= quantidade:
#                             # Descontar do estoque se houver quantidade suficiente
#                             produto.quantidade_estoque -= quantidade
#                             produto.save()
#                         else:
#                             # Se não houver quantidade suficiente, retornar erro
#                             return JsonResponse({'success': False, 'message': 'Estoque insuficiente para um dos produtos.'}, status=400)

#                     # Salvar os produtos na venda
#                     ProdutoCaixaPdv.objects.create(
#                         caixa_pdv=caixa_pdv,
#                         produto=produto,
#                         quantidade=quantidade,
#                         preco_unitario=produto.preco_de_venda,
#                         total=quantidade * produto.preco_de_venda
#                     )

#             # Liberar a mesa
#             mesa.status = 'livre'
#             mesa.save()

#             # Marcar a comanda como fechada
#             comanda.status = 'fechada'
#             comanda.save()

#             # Retornar uma resposta de sucesso
#             return JsonResponse({'success': True, 'message': 'Comanda convertida para venda direta e finalizada com sucesso!'})

#         except Exception as e:
#             # Se ocorrer algum erro, retornar uma mensagem de erro
#             return JsonResponse({'success': False, 'message': str(e)})

#     # Se não for uma requisição POST, redirecionar para a lista de mesas
#     return redirect('listar_mesas')

def fechar_comanda(request, mesa_id):
    if request.method == 'POST':
        try:
            # Capturar os dados da requisição
            data = json.loads(request.body)
            numero_pedido = data.get('numero_pedido')
            vendedor_id = data.get('vendedor_id')
            cliente_id = data.get('cliente_id')
            desconto = data.get('desconto', 0.0)
            total = data.get('total')
            payment_method = data.get('payment_method')
            produtos = data.get('produtos', [])

            # Buscar a mesa e a comanda aberta associada
            mesa = get_object_or_404(Mesa, id=mesa_id)
            comanda = get_object_or_404(Comanda, mesa=mesa, status='aberta')

            # Verificar se há um caixa aberto, considerando o gerenciamento de caixa
            configuracao = Configuracao.objects.first()
            gerenciar_caixa = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False

            # Pega o caixa aberto para associar a venda, se o gerenciamento estiver ativado
            caixa = None
            if gerenciar_caixa:
                caixa = Caixa.objects.filter(status='Aberto').first()
                if not caixa:
                    return JsonResponse({'success': False, 'message': 'Não há caixa aberto para registrar a venda.'}, status=400)

            # Verifica se o cliente e o vendedor existem
            cliente = Cliente.objects.filter(id=cliente_id).first()
            vendedor = User.objects.filter(id=vendedor_id).first()

            if not cliente or not vendedor:
                return JsonResponse({'success': False, 'message': 'Cliente ou Vendedor não encontrado.'}, status=404)

            # Criando a venda (CaixaPdv) e associando ao caixa se ele estiver aberto
            caixa_pdv = CaixaPdv.objects.create(
                caixa=caixa,  # Associa ao caixa aberto, se existir
                numero_pedido=numero_pedido,
                vendedor=vendedor,
                cliente=cliente,
                desconto=desconto,
                total=total,
                status="Finalizado",  # Marcar como finalizado direto ao fechar a comanda
                payment_method=payment_method
            )

            # Processar os produtos e salvar no CaixaPdv
            for produto_data in produtos:
                produto = Produto.objects.filter(id=produto_data.get('produto_id')).first()

                if produto:
                    quantidade = produto_data['quantidade']

                    # Verificar se o controle de estoque está ativado
                    if produto.controle_estoque:
                        if produto.quantidade_estoque >= quantidade:
                            # Descontar do estoque se houver quantidade suficiente
                            produto.quantidade_estoque -= quantidade
                            produto.save()
                        else:
                            # Se não houver quantidade suficiente, retornar erro
                            return JsonResponse({'success': False, 'message': 'Estoque insuficiente para um dos produtos.'}, status=400)

                    # Salvar os produtos na venda
                    ProdutoCaixaPdv.objects.create(
                        caixa_pdv=caixa_pdv,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.preco_de_venda,
                        total=quantidade * produto.preco_de_venda
                    )

            # Liberar a mesa
            mesa.status = 'livre'
            mesa.save()

            # Marcar a comanda como fechada
            comanda.status = 'fechada'
            comanda.save()

            # Retornar uma resposta de sucesso
            return JsonResponse({'success': True, 'message': 'Comanda convertida para venda direta e finalizada com sucesso!'})

        except Exception as e:
            # Se ocorrer algum erro, retornar uma mensagem de erro
            return JsonResponse({'success': False, 'message': str(e)})

    # Se não for uma requisição POST, redirecionar para a lista de mesas
    return redirect('listar_mesas')


# Pagina de hístórico de vendas
def historico_vendas(request):
    vendas = Comanda.objects.filter(status='fechada').order_by('-created_at')  # Filtra apenas as comandas fechadas
    return render(request, 'comanda/lista_vendas_comanda.html', {'vendas': vendas})

#  Veja os detalhes da comanda
def detalhes_comanda(request, comanda_id):
    try:
        # Buscar a comanda com seus produtos
        comanda = Comanda.objects.get(id=comanda_id)
        produtos_comanda = ProdutoComanda.objects.filter(comanda=comanda)

        # Estrutura para enviar os dados para o frontend
        produtos = [{
            'nome': produto_comanda.produto.nome,
            'quantidade': produto_comanda.quantidade,
            'preco_unitario': produto_comanda.preco_unitario,
            'total': produto_comanda.total
        } for produto_comanda in produtos_comanda]

        # Dados da comanda
        dados_comanda = {
            'numero_pedido': comanda.numero_pedido,
            'vendedor': comanda.vendedor.username,
            'cliente': comanda.cliente.nome,
            'total': comanda.total,
            'desconto': comanda.desconto,
            'payment_method': comanda.payment_method,
            'produtos': produtos
        }

        return JsonResponse({'success': True, 'data': dados_comanda})

    except Comanda.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comanda não encontrada.'})

#  Exluir a comanda criada
def excluir_comanda(request, comanda_id):
    try:
        # Recupera a comanda
        comanda = Comanda.objects.get(id=comanda_id)
        
        # Recupera todos os produtos da comanda
        produtos_comanda = ProdutoComanda.objects.filter(comanda=comanda)
        
        # Para cada produto na comanda, repor estoque se for gerenciável
        for produto_comanda in produtos_comanda:
            produto = produto_comanda.produto  # Produto relacionado à comanda

            # Verifica se o produto é gerenciável no estoque
            if produto.controle_estoque:
                # Repor a quantidade de estoque do produto
                produto.quantidade_estoque += produto_comanda.quantidade
                produto.save()  # Salva as alterações no estoque

        # Exclui a comanda
        comanda.delete()

        return JsonResponse({"success": True, "message": "Comanda excluída com sucesso."})
    except Comanda.DoesNotExist:
        return JsonResponse({"success": False, "message": "Comanda não encontrada."})

def adicionar_produto_comanda(request, mesa_id):
    if request.method == 'POST':
        try:
            # Buscar a mesa e a comanda associada
            mesa = get_object_or_404(Mesa, id=mesa_id)
            comanda = get_object_or_404(Comanda, mesa=mesa, status='aberta')

            # Carregar os dados do corpo da requisição como JSON
            data = json.loads(request.body)
            produtos = data.get('produtos', [])

            # Obter os IDs dos produtos enviados
            produtos_enviados_ids = [item.get('produto_id') for item in produtos]

            # Iterar sobre os produtos enviados e processar cada um
            for item in produtos:
                produto_id = item.get('produto_id')
                quantidade = int(item.get('quantidade', 1))  # Quantidade padrão é 1

                # Buscar o produto no banco de dados
                produto = get_object_or_404(Produto, id=produto_id)
                preco_unitario = produto.preco_de_venda  # Ajuste o nome do campo aqui

                # Verificar se o produto já existe na comanda
                produto_comanda = ProdutoComanda.objects.filter(comanda=comanda, produto=produto).first()

                if produto_comanda:
                    # Se o produto já existe, ajustar a quantidade
                    if quantidade == 0:
                        # Se a quantidade for zero, remover o produto da comanda
                        produto_comanda.delete()
                    else:
                        # Se a quantidade for maior que zero, atualizar a quantidade e o total
                        produto_comanda.quantidade = quantidade
                        produto_comanda.total = produto_comanda.quantidade * preco_unitario
                        produto_comanda.save()
                else:
                    # Se o produto não existir na comanda, criar um novo registro
                    if quantidade > 0:
                        ProdutoComanda.objects.create(
                            comanda=comanda,
                            produto=produto,
                            quantidade=quantidade,
                            preco_unitario=preco_unitario,
                            total=quantidade * preco_unitario
                        )

            # Remover os produtos da comanda que não foram enviados na requisição
            produtos_na_comanda = ProdutoComanda.objects.filter(comanda=comanda)
            for produto_comanda in produtos_na_comanda:
                if produto_comanda.produto.id not in produtos_enviados_ids:
                    produto_comanda.delete()

            # Atualizar o total da comanda
            comanda.total = sum(item.total for item in ProdutoComanda.objects.filter(comanda=comanda))
            comanda.save()

            # Responder com sucesso
            return JsonResponse({'success': True, 'message': 'Produtos atualizados com sucesso!'})

        except Exception as e:
            # Se ocorrer algum erro, retornar uma mensagem de erro
            return JsonResponse({'success': False, 'message': str(e)})

    # Se não for uma requisição POST, redirecionar para a lista de mesas
    return redirect('listar_mesas')

def get_comanda_details(request, mesa_id):
    # Buscar a mesa com o ID fornecido
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Buscar a comanda associada à mesa
    comanda = get_object_or_404(Comanda, mesa=mesa, status='aberta')

    # Buscar os produtos relacionados a essa comanda
    produtos = ProdutoComanda.objects.filter(comanda=comanda)

    # Estruturar os dados que serão retornados
    data = {
        'id': comanda.id,
        'numero_pedido': comanda.numero_pedido,
        'vendedor': {
            'id': comanda.vendedor.id,
            'nome': comanda.vendedor.username,  # Ajuste conforme necessário
        },
        'status': comanda.status,
        'desconto': comanda.desconto,
        'total': comanda.total,
        'payment_method': comanda.payment_method,
        'produtos': [{
            'produto': {
                'id': produto.produto.id,
                'nome': produto.produto.nome,
                'codigoBarras': produto.produto.codigo_barras or "",
                'file': produto.produto.file.url if produto.produto.file else None,
                'categoria': {
                    'nome': produto.produto.categoria.nome if produto.produto.categoria else None,
                    'file': produto.produto.categoria.file.url if produto.produto.categoria and produto.produto.categoria.file else None
                } if produto.produto.categoria else None,
            },
            'quantidade': produto.quantidade,
            'preco_unitario': produto.preco_unitario,
            'total': produto.total,
        } for produto in produtos]
    }

    return JsonResponse(data)

def listar_mesas(request):
    mesas = Mesa.objects.all()  # Obter todas as mesas
    form = MesaForm()  # Formulário vazio para cadastro
    return render(request, 'comanda/listar_mesas.html', {'mesas': mesas, 'form': form})
    
def cadastrar_mesa(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()  # Salva a nova mesa no banco de dados
            return redirect('listar_mesas')  # Redireciona para a página de listagem das mesas
    else:
        form = MesaForm()  # Cria um formulário vazio
    return render(request, 'comanda/cadastrar_mesa.html', {'form': form})

#  Excluir a mesa
def excluir_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)  # Encontra a mesa ou retorna 404 se não existir

    # Se a mesa estiver livre, exclui a mesa
    mesa.delete()

    # Exibe uma mensagem de sucesso após a exclusão
    messages.success(request, f"A mesa {mesa.nome} foi excluída com sucesso.")
    return redirect('listar_mesas')  # Redireciona para a página de listagem das mesas

# Abra uma comanda ou continue editando depois
def abrir_ou_gerenciar_comanda(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    # Pega a configuração do cliente padrão
    configuracao = Configuracao.objects.first()
    cliente_padrao = configuracao.cliente_padrao if configuracao else None

    # Verifica se já existe uma comanda associada à mesa
    comanda_existente = Comanda.objects.filter(mesa=mesa, status='aberta').first()

    if comanda_existente:
        # Se já existir uma comanda aberta, redireciona para a página de gerenciamento da comanda
        # Passa o ID da mesa e o cliente padrão para o template
        return render(request, 'comanda/caixa_comanda.html', {
            'mesa_id': mesa.id,
            'mesa_nome': mesa.nome,
            'cliente_padrao': cliente_padrao
        })
    
    if mesa.status == 'livre':
        # Se a mesa estiver livre, cria uma nova comanda
        mesa.status = 'ocupada'
        mesa.save()

        # Gera o número do pedido único
        numero_pedido = gerar_numero_pedido()

        # Criação de uma nova comanda associada à mesa e ao vendedor (usuário autenticado)
        comanda = Comanda.objects.create(
            numero_pedido=numero_pedido,  # Adiciona o número do pedido gerado
            mesa=mesa,
            status='aberta',
            vendedor=request.user  # Atribuindo o vendedor como o usuário logado
        )

        # Redireciona para a página de gerenciamento da comanda, passando a comanda e o cliente padrão
        return render(request, 'comanda/caixa_comanda.html', {
            'comanda': comanda,
            'mesa_nome': mesa.nome,
            'cliente_padrao': cliente_padrao
        })

    # Se a mesa não estiver livre, redireciona para a lista de mesas
    return redirect('listar_mesas')

# Gera o Numero do pedido automaticamente
def gerar_numero_pedido():
    # Gera um número aleatório de 8 dígitos
    numero_aleatorio = random.randint(10000000, 99999999)
    
    # Formata o número de pedido
    numero_pedido = f"PDV-{numero_aleatorio}"

    return numero_pedido


