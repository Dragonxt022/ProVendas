from django.shortcuts import render, redirect, get_object_or_404
from .models import Configuracao
from .forms import ConfiguracaoForm

def listar_configuracao(request):
    # Obter ou criar a configuração
    configuracao, created = Configuracao.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, request.FILES, instance=configuracao)
        if form.is_valid():
            form.save()

            return redirect('listar_configuracao')
    else:
        form = ConfiguracaoForm(instance=configuracao)

    # Passando os dados para a template para renderizar o formulário
    return render(request, 'configuracoes/listar_configuracao.html', {
        'form': form,
        'configuracao': configuracao
    })
