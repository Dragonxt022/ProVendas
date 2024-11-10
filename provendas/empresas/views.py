
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmpresaForm
from .models import Empresa
from django.contrib import messages

# View para gerenciar empresas
def listar_empresas(request):
    empresas = Empresa.objects.all()
    form = EmpresaForm()
    return render(request, 'empresas/listar_empresas.html', {'empresas': empresas, 'form': form})

def cadastrar_empresa(request):
    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        
        # Se o ID da empresa estiver presente, vamos editar
        if empresa_id:  
            empresa = get_object_or_404(Empresa, id=empresa_id)
            form = EmpresaForm(request.POST, instance=empresa)  # Edita a empresa existente
            action = "atualizada"
        else:
            form = EmpresaForm(request.POST)  # Cria uma nova empresa
            action = "cadastrada"

        if form.is_valid():
            empresa_salva = form.save()  # Salva a empresa (nova ou editada)
            messages.success(request, f'empresa "{empresa_salva.nome_empresa}" {action} com sucesso!')
            return redirect('listar_empresas')  # Redireciona após salvar

    # Caso não seja um POST ou o formulário não seja válido, recarrega a lista de empresas
    empresas = Empresa.objects.all()
    form = EmpresaForm()  # Reinicializa o formulário para exibir vazio
    return render(request, 'empresas/listar_empresas.html', {'empresas': empresas, 'form': form})

def excluir_empresa(request, empresa_id):
    print(f"ID da empresa recebida para exclusão: {empresa_id}")  # Adicione esta linha para verificar o ID

    empresa = get_object_or_404(Empresas, id=empresa_id)
    empresa.delete()
    messages.success(request, f'empresa "{empresa.nome_empresa}" excluída com sucesso!')
    return redirect('listar_empresas')

