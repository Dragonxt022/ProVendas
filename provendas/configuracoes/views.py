from django.shortcuts import render, redirect
from .models import Configuracao
from .forms import ConfiguracaoForm

def listar_configuracao(request):
    configuracao, created = Configuracao.objects.get_or_create(id=1)  # Assumindo que há uma única configuração

    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, request.FILES, instance=configuracao)
        if form.is_valid():
            form.save()
            return redirect('listar_configuracao')  # Redireciona após salvar
    else:
        form = ConfiguracaoForm(instance=configuracao)

    return render(request, 'configuracoes/listar_configuracao.html', {'form': form})
