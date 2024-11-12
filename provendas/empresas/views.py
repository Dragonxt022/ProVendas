from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmpresaForm
from .models import Empresa
from django.contrib import messages

# View para listar e gerenciar empresas
def listar_empresas(request):
    empresas = Empresa.objects.all()
    form = EmpresaForm()  # Formulário vazio para o modal de cadastro/edição

    # Passa a lista de estados para o contexto
    estados_brasil = Empresa.ESTADOS_BRASIL

    # Se for uma requisição POST, significa que o usuário está cadastrando ou editando uma empresa
    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')

        # Se o ID da empresa estiver presente, trata-se de uma edição
        if empresa_id:
            empresa = get_object_or_404(Empresa, id=empresa_id)
            form = EmpresaForm(request.POST, instance=empresa)
            action = "atualizada"
        else:
            form = EmpresaForm(request.POST)  # Nova empresa
            action = "cadastrada"

        if form.is_valid():
            empresa_salva = form.save()
            messages.success(request, f'Empresa "{empresa_salva.nome_empresa}" {action} com sucesso!')
            return redirect('listar_empresas')  # Redireciona para a lista de empresas após o sucesso

    return render(request, 'empresas/listar_empresas.html', {
        'empresas': empresas,
        'form': form,
        'estados_brasil': estados_brasil
    })
# View para excluir uma empresa
def excluir_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.delete()
    messages.success(request, f'Empresa "{empresa.nome_empresa}" excluída com sucesso!')
    return redirect('listar_empresas')
