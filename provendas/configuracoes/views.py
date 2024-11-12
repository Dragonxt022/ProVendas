from django.shortcuts import render, redirect
from .models import Configuracao
from .forms import ConfiguracaoForm

def listar_configuracao(request):
    configuracao = Configuracao.objects.first()  # Supondo que haja uma única configuração
    if not configuracao:
        configuracao = Configuracao.objects.create()  # Caso não haja, cria uma nova

    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, instance=configuracao)
        if form.is_valid():
            form.save()
            return redirect('listar_configuracao')  # Redireciona para evitar resubmissão do formulário
    else:
        form = ConfiguracaoForm(instance=configuracao)

    return render(request, 'configuracoes/listar_configuracao.html', {'form': form})
