# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import UsuarioForm
from .models import Perfil

def listar_usuarios(request):
    usuarios = User.objects.all()  # Lista todos os usuários
    grupos = Group.objects.all()

    # Lógica de cadastro ou atualização de usuário
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')  # Obtém o ID do usuário
        if usuario_id:  # Se o ID existir, estamos atualizando um usuário
            usuario = User.objects.get(id=usuario_id)
            form = UsuarioForm(request.POST, request.FILES, instance=usuario)  # Preenche o formulário com os dados do usuário existente
        else:  # Se o ID não existir, estamos criando um novo usuário
            form = UsuarioForm(request.POST, request.FILES)  # Formulário para novo usuário

        if form.is_valid():
            usuario_salvo = form.save(commit=False)

            # Definindo a senha do novo usuário se não for especificada
            nova_senha = form.cleaned_data.get('nova_senha')
            if nova_senha:
                usuario_salvo.set_password(nova_senha)  # Setando a senha

            usuario_salvo.save()  # Salva o usuário no banco de dados

            # Se for um novo usuário, salvar o perfil
            perfil, created = Perfil.objects.get_or_create(user=usuario_salvo)  # Obtém ou cria o perfil
            if 'foto_perfil' in request.FILES:
                perfil.foto_perfil = request.FILES['foto_perfil']  # Atribui a foto do perfil se fornecida
            perfil.save()

            # Associando os grupos do formulário ao usuário
            grupos_selecionados = form.cleaned_data.get('grupos')
            usuario_salvo.groups.set(grupos_selecionados)

            # Se a senha foi alterada, força o logout do usuário atual
            if usuario_id == str(request.user.id) and nova_senha:
                logout(request)  # Desloga o usuário para que ele precise se logar novamente com a nova senha
                messages.success(request, f'Sua senha foi alterada com sucesso. Por favor, faça login novamente.')

            if usuario_id:
                messages.success(request, f'Usuário "{usuario_salvo.username}" atualizado com sucesso!')
            else:
                messages.success(request, f'Usuário "{usuario_salvo.username}" criado com sucesso!')

            return redirect('listar_usuarios')  # Redireciona para a mesma página após salvar

    else:
        form = UsuarioForm()  # Formulário vazio para novo cadastro

    return render(request, 'usuarios/listar_usuarios.html', {'form': form, 'usuarios': usuarios, 'grupos': grupos})


# Excluir usuário
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('listar_usuarios')
