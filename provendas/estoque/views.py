# estoque/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoriaProdutoForm, ProdutoForm
from .models import CategoriaProduto, Produto
from django.contrib import messages
from django.http import HttpResponse
import csv 
from django.http import JsonResponse
from django.utils.text import slugify
import uuid


# Importador e exportador
def importar_produtos(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        arquivo = request.FILES['csv_file']

        try:
            csv_file = csv.reader(arquivo.read().decode('utf-8').splitlines())
            next(csv_file)  # Ignora o cabeçalho

            for row in csv_file:
                # Atribui os valores das colunas ou define padrões se estiverem ausentes
                produto_id = row[0] or str(uuid.uuid4())  # Gera um ID automático se não houver
                nome = row[1] or ''
                codigo_barras = row[2] or ''
                preco_de_venda = float(row[3]) if row[3] else 0.0  # Define 0.0 se estiver vazio
                preco_de_custo = float(row[4]) if row[4] else 0.0  # Define 0.0 se estiver vazio
                quantidade_estoque = int(row[5]) if row[5] else 0  # Define 0 se estiver vazio
                categoria_nome = row[6] or ''  # Categoria deve ser fornecida
                status = row[7].lower() if row[7] else 'ativado'  # Define como 'ativado' se estiver vazio
                controle_estoque = row[8].lower() == 'sim' if row[8] else False  # Define como False se estiver vazio

                # Verifica se o nome, categoria e preço de venda são fornecidos
                if not nome or not categoria_nome or preco_de_venda <= 0:
                    messages.warning(request, f'Dados insuficientes para o produto: {nome}.')
                    continue  # Pula para o próximo produto se os dados obrigatórios estiverem ausentes

                # Verifica se a categoria já existe, caso contrário cria uma nova
                categoria, created = CategoriaProduto.objects.get_or_create(nome=categoria_nome)

                # Atualiza ou cria o produto
                produto, created = Produto.objects.update_or_create(
                    id=produto_id,
                    defaults={
                        'nome': nome,
                        'codigo_barras': codigo_barras,
                        'preco_de_venda': preco_de_venda,
                        'preco_de_custo': preco_de_custo,
                        'quantidade_estoque': quantidade_estoque,
                        'categoria': categoria,
                        'status': status,
                        'controle_estoque': controle_estoque,
                    }
                )

                # Mensagem se o produto foi atualizado
                if not created:
                    messages.info(request, f'O produto "{nome}" foi atualizado.')

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
            produto.preco_de_custo,
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


def cadastrar_categoria_ajax(request):
    if request.method == 'POST':
        nome_categoria = request.POST.get('nome')

        # Verifica se a categoria já existe
        if CategoriaProduto.objects.filter(nome=nome_categoria).exists():
            return JsonResponse({"error": "Categoria já existe!"}, status=400)
        
        # Criação de uma nova categoria
        form = CategoriaProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            categoria_salva = form.save()
            
            # Retorna a mensagem de sucesso junto com os dados da categoria
            return JsonResponse({
                "id": categoria_salva.id,
                "nome": categoria_salva.nome,
                "message": "Categoria cadastrada com sucesso!"
            }, status=200)
        else:
            return JsonResponse({"error": "Erro no formulário!"}, status=400)

def excluir_categoria(request, categoria_id):
    print(f"ID da categoria recebida para exclusão: {categoria_id}")  # Adicione esta linha para verificar o ID

    categoria = get_object_or_404(CategoriaProduto, id=categoria_id)
    categoria.delete()
    messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso!')
    return redirect('listar_categorias')

# View para gerenciar produtos
def listar_produtos(request):
    produtos = Produto.objects.all()
    categorias = CategoriaProduto.objects.all()

    if request.method == 'POST':
        # Obter os dados do formulário
        produto_id = request.POST.get('produto_id')  # Captura o ID do produto se existir
        codigo_barras = request.POST.get('codigo_barras')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        preco_de_venda = float(request.POST.get('preco_de_venda').replace(',', '.')) if request.POST.get('preco_de_venda') else 0.0
        preco_de_custo = float(request.POST.get('preco_de_custo').replace(',', '.')) if request.POST.get('preco_de_custo') else 0.0
        quantidade_estoque = int(request.POST.get('quantidade_estoque')) if request.POST.get('quantidade_estoque') else 0
        categoria_id = request.POST.get('categoria')
        status = request.POST.get('status')
        file = request.FILES.get('file')
        controle_estoque = 1 if request.POST.get('controle_estoque') == 'on' else 0

        # Tenta encontrar o produto pelo ID
        produto = Produto.objects.filter(id=produto_id).first() if produto_id else None

        if produto:
            # Se o produto existir, atualize os campos
            produto.codigo_barras = codigo_barras
            produto.nome = nome
            produto.descricao = descricao
            produto.preco_de_venda = preco_de_venda
            produto.preco_de_custo = preco_de_custo
            produto.quantidade_estoque = quantidade_estoque
            produto.categoria_id = categoria_id
            produto.status = status
            if file:
                produto.file = file
            produto.controle_estoque = controle_estoque
            messages.success(request, 'Produto atualizado com sucesso.')
        else:
            # Se o produto não existir, crie um novo
            produto = Produto(
                codigo_barras=codigo_barras,
                nome=nome,
                descricao=descricao,
                preco_de_venda=preco_de_venda,
                preco_de_custo=preco_de_custo,
                quantidade_estoque=quantidade_estoque,
                categoria_id=categoria_id,
                status=status,
                file=file,
                controle_estoque=controle_estoque,
            )
            messages.success(request, 'Produto criado com sucesso.')

        produto.save()
        return redirect('listar_produtos')

    return render(request, 'estoque/produto/listar_produtos.html', {
        'produtos': produtos,
        'categorias': categorias,
    })


def editar_produto(request, produto_id):  # Recebe o ID do produto na URL
    produto = get_object_or_404(Produto, id=produto_id)  # Obtém o produto pelo ID

    if request.method == 'POST':
        # Atualiza todos os campos do produto
        produto.codigo_barras = request.POST.get('codigo_barras')
        produto.nome = request.POST.get('nome')
        produto.descricao = request.POST.get('descricao')

        # Converte o valor de `preco_de_venda` e `preco_de_custo` para decimal
        preco_de_venda = request.POST.get('preco_de_venda').replace(',', '.') if request.POST.get('preco_de_venda') else '0'
        produto.preco_de_venda = float(preco_de_venda)

        preco_de_custo = request.POST.get('preco_de_custo').replace(',', '.') if request.POST.get('preco_de_custo') else '0'
        produto.preco_de_custo = float(preco_de_custo)

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
    try:
        # Tenta obter e excluir o produto
        produto = Produto.objects.get(id=produto_id)
        produto.delete()
        messages.success(request, "Produto excluído com sucesso!")
    except Produto.DoesNotExist:
        # Caso o produto já tenha sido excluído
        messages.warning(request, "O produto já foi excluído ou não existe.")
    return redirect('listar_produtos')