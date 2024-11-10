# estoque/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaProdutoForm, ProdutoForm
from .models import CategoriaProduto, Produto
from django.contrib import messages
from django.http import HttpResponse
import csv 



# Importador e exportador
def importar_produtos(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        arquivo = request.FILES['csv_file']
        
        # Lê o arquivo CSV
        try:
            csv_file = csv.reader(arquivo.read().decode('utf-8').splitlines())
            next(csv_file)  # Ignora o cabeçalho

            for row in csv_file:
                produto_id = row[0]  # O ID do produto estará na primeira coluna
                nome = row[1]
                codigo_barras = row[2]
                preco_de_venda = row[3]
                preco_de_cursto = row[4]
                quantidade_estoque = row[5]
                categoria_nome = row[6]  # Nome da categoria na posição 6
                status = row[7]  # Status (ativado/desativado) na posição 7
                controle_estoque = row[8].lower() == 'sim'  # Controle de Estoque na posição 8 (Sim/Não)

                # Verifica se a categoria já existe, caso contrário cria uma nova
                categoria, created = CategoriaProduto.objects.get_or_create(nome=categoria_nome)
                
                # Tenta encontrar o produto pelo ID. Se não encontrar, cria um novo
                produto, created = Produto.objects.update_or_create(
                    id=produto_id,  # Identifica o produto pelo ID
                    defaults={
                        'nome': nome,
                        'codigo_barras': codigo_barras,
                        'preco_de_venda': preco_de_venda,
                        'preco_de_cursto': preco_de_cursto,
                        'quantidade_estoque': quantidade_estoque,
                        'categoria': categoria,
                        'status': status,
                        'controle_estoque': controle_estoque,
                    }
                )

                # Mensagem opcional, se o produto foi atualizado
                if not created:
                    messages.info(request, f'O produto {nome} foi atualizado.')

            messages.success(request, 'Produtos importados com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao importar produtos: {e}')
        return redirect('listar_produtos')

    return render(request, 'estoque/produto/listar_produtos.html')

def exportar_produtos(request):
    produtos = Produto.objects.all()

    # Cria a resposta HTTP para download de CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produtos.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nome', 'Código de Barras', 'Preço de Venda', 'Preço de Custo', 'Quantidade em Estoque', 'Categoria', 'Status', 'Controle de Estoque'])

    for produto in produtos:
        writer.writerow([
            produto.id,
            produto.nome,
            produto.codigo_barras,
            produto.preco_de_venda,
            produto.preco_de_cursto,
            produto.quantidade_estoque,
            produto.categoria.nome,
            produto.status,
            'Sim' if produto.controle_estoque else 'Não',
        ])
    
    return response

# View para gerenciar Categorias
def listar_categorias(request):
    categorias = CategoriaProduto.objects.all()
    form = CategoriaProdutoForm()
    return render(request, 'estoque/categoria/cadastrar_categoria.html', {'categorias': categorias, 'form': form})

def cadastrar_categoria(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        
        if categoria_id:
            categoria = get_object_or_404(CategoriaProduto, id=categoria_id)
            form = CategoriaProdutoForm(request.POST, request.FILES, instance=categoria)
            action = "atualizada"
        else:
            form = CategoriaProdutoForm(request.POST, request.FILES)
            action = "cadastrada"

        if form.is_valid():
            categoria_salva = form.save()
            messages.success(request, f'Categoria "{categoria_salva.nome}" {action} com sucesso!')
            return redirect('listar_categorias')

    categorias = CategoriaProduto.objects.all()
    form = CategoriaProdutoForm()
    return render(request, 'estoque/categoria/cadastrar_categoria.html', {'categorias': categorias, 'form': form})

def excluir_categoria(request, categoria_id):
    print(f"ID da categoria recebida para exclusão: {categoria_id}")  # Adicione esta linha para verificar o ID

    categoria = get_object_or_404(CategoriaProduto, id=categoria_id)
    categoria.delete()
    messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso!')
    return redirect('listar_categorias')

# View para gerenciar produtos
def listar_produtos(request):
    produtos = Produto.objects.all()
    categorias = CategoriaProduto.objects.all()  # Busca todas as categorias para o select

    if request.method == 'POST':
        # Obter os dados do formulário
        codigo_barras = request.POST.get('codigo_barras')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        preco_de_venda = request.POST.get('preco_de_venda')
        preco_de_cursto = request.POST.get('preco_de_cursto')
        quantidade_estoque = request.POST.get('quantidade_estoque')
        categoria_id = request.POST.get('categoria')
        status = request.POST.get('status')
        file = request.FILES.get('file')
        controle_estoque = 1 if request.POST.get('controle_estoque') == 'on' else 0  # Muda para 1 ou 0


        # Conversão de valores sem validação
        preco_de_venda = float(preco_de_venda.replace(',', '.')) if preco_de_venda else 0.0  # Converter preço de venda para float
        preco_de_cursto = float(preco_de_cursto.replace(',', '.')) if preco_de_cursto else 0.0  # Converter preço de custo para float
        quantidade_estoque = int(quantidade_estoque) if quantidade_estoque else 0  # Converter quantidade em estoque para int

        # Criação de um novo produto
        produto = Produto(
            codigo_barras=codigo_barras,
            nome=nome,
            descricao=descricao,
            preco_de_venda=preco_de_venda,
            preco_de_cursto=preco_de_cursto,
            quantidade_estoque=quantidade_estoque,
            categoria_id=categoria_id,
            status=status,
            file=file,
            controle_estoque=controle_estoque,  # Adiciona o controle de estoque aqui

        )
        produto.save()
        messages.success(request, 'Produto criado com sucesso.')
        return redirect('listar_produtos')

    return render(request, 'estoque/produto/listar_produtos.html', {
        'produtos': produtos,
        'categorias': categorias,  # Passa as categorias para o template
    })

def editar_produto(request, produto_id):  # Recebe o ID do produto na URL
    produto = get_object_or_404(Produto, id=produto_id)  # Obtém o produto pelo ID

    if request.method == 'POST':
        # Atualiza todos os campos do produto
        produto.codigo_barras = request.POST.get('codigo_barras')
        produto.nome = request.POST.get('nome')
        produto.descricao = request.POST.get('descricao')

        # Converte o valor de `preco_de_venda` e `preco_de_cursto` para decimal
        preco_de_venda = request.POST.get('preco_de_venda').replace(',', '.') if request.POST.get('preco_de_venda') else '0'
        produto.preco_de_venda = float(preco_de_venda)

        preco_de_cursto = request.POST.get('preco_de_cursto').replace(',', '.') if request.POST.get('preco_de_cursto') else '0'
        produto.preco_de_cursto = float(preco_de_cursto)

        # Atualiza a quantidade em estoque, convertendo para int
        quantidade_estoque = request.POST.get('quantidade_estoque')
        produto.quantidade_estoque = int(quantidade_estoque) if quantidade_estoque else 0

        produto.categoria_id = request.POST.get('categoria')
        produto.status = request.POST.get('status')

        # Se houver um novo arquivo, atualiza o campo 'file'
        if 'file' in request.FILES:
            produto.file = request.FILES['file']

        produto.save()

        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('listar_produtos')

    # Se não for POST, renderiza o formulário com os dados do produto
    return render(request, 'estoque/produto/listar_produtos.html', {
        'produto': produto,
    })

def excluir_produto(request, produto_id):
    # Tenta obter a categoria pelo ID, retornando 404 se não existir
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    return redirect('listar_produtos')