# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse


from .models import Cliente
from .forms import ClienteForm

def listar_clientes(request):
    clientes = Cliente.objects.all()  # Busca todos os clientes cadastrados
    form = ClienteForm()

    # Formatar a data de nascimento de cada cliente para o formato ISO 'YYYY-MM-DD'
    for cliente in clientes:
        if cliente.data_nascimento:
            cliente.data_nascimento = cliente.data_nascimento.strftime('%Y-%m-%d')  # Formato ISO

    return render(request, 'clientes/listar_clientes.html', {'clientes': clientes, 'form': form})

def editar_cliente(request, cliente_id):
    # Obtém o cliente com o ID fornecido na URL
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            # Atualiza o cliente sem tratar campos de limite de crédito
            form.save()
            messages.success(request, 'Cliente editado com sucesso!')
            return redirect('listar_clientes')
        else:
            print(form.errors)  # Ajuda a depurar caso o formulário tenha erros
    
    return redirect('listar_clientes')


def cadastrar_cliente(request):
    if request.method == 'POST':
        # Captura os dados diretamente do request.POST
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        data_nascimento = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        status = request.POST.get('status')
        
        # Criação de um novo cliente sem campos de limite de crédito
        cliente = Cliente(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            status=status
        )
        cliente.save()

        # Mensagem de sucesso
        messages.success(request, f'Cliente "{nome}" cadastrado com sucesso!')
        return redirect('listar_clientes')  # Redireciona para a lista de clientes

    return redirect('listar_clientes')


def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, f'O cliente {cliente.nome} foi excluído com sucesso.')
        return redirect(reverse('listar_clientes'))  # Substitua 'listar_clientes' pelo nome da view de listagem de clientes.
    return redirect(reverse('listar_clientes'))