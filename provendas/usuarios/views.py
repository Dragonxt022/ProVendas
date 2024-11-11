# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import UsuarioForm
from .models import Perfil

# Listar usuários
def listar_usuarios(request):
    form = UsuarioForm()  # Inicializa o formulário para criação de usuário
    usuarios = User.objects.all()  # Lista todos os usuários
    grupos = Group.objects.all()

    
    for usuario in usuarios:
        # Carrega o perfil associado a cada usuário
        usuario.perfil = Perfil.objects.filter(user=usuario).first()  # Atribui o perfil do usuário
    return render(request, 'usuarios/listar_usuarios.html', {'form': form, 'usuarios': usuarios, 'grupos': grupos})

# Criar ou atualizar usuário
def cadastrar_atualizar_usuario(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')

        # Se o ID do usuário estiver presente, editar o usuário existente
        if usuario_id:
            usuario = get_object_or_404(User, id=usuario_id)
            form = UsuarioForm(request.POST, request.FILES, instance=usuario)  # Inclui request.FILES
            action = "atualizado"
        else:
            form = UsuarioForm(request.POST, request.FILES)  # Cria um novo usuário, inclui request.FILES
            action = "cadastrado"

        if form.is_valid():
            usuario_salvo = form.save(commit=False)

            # Define uma senha padrão ao criar um novo usuário
            if not usuario_id:
                usuario_salvo.set_password('password')  # Aqui define a senha padrão para novos usuários

            usuario_salvo.save()  # Salva o usuário primeiro

            # Atualiza ou cria o perfil com a foto de perfil, se necessário
            if usuario_id:  # Se for uma edição, atualiza o perfil existente
                perfil = get_object_or_404(Perfil, user=usuario_salvo)
                if 'foto_perfil' in request.FILES:  # Verifica se uma nova imagem foi enviada
                    perfil.foto_perfil = request.FILES['foto_perfil']  # Atribui a nova imagem
                perfil.save()  # Salva o perfil atualizado
            else:  # Se for um novo usuário, cria um novo perfil
                perfil = Perfil(user=usuario_salvo)
                if 'foto_perfil' in request.FILES:
                    perfil.foto_perfil = request.FILES['foto_perfil']
                perfil.save()  # Salva o novo perfil

            # Adiciona os grupos do formulário
            grupos_selecionados = form.cleaned_data.get('grupos')
            usuario_salvo.groups.set(grupos_selecionados)  # Define os novos grupos

            # Retorna a mensagem de sucesso e redireciona
            messages.success(request, f'Usuário "{usuario_salvo.username}" {action} com sucesso!')
            return redirect('listar_usuarios')  # Redireciona para a lista de usuários

    # Caso não seja um POST ou o formulário não seja válido, recarrega a lista de usuários
    usuarios = User.objects.all()
    grupos = Group.objects.all()  # Obtém todos os grupos
    form = UsuarioForm()  # Reinicializa o formulário para exibir vazio
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios, 'form': form, 'grupos': grupos})

# Excluir usuário
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('listar_usuarios')
