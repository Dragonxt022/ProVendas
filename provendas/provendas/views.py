from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    # Verifica se o usuário já está autenticado
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redireciona para o dashboard

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redireciona para a página inicial após o login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'index.html')  # Substitua 'index.html' pelo nome do template principal
