from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import LicenseKey
import re
from django.contrib.auth.models import User
from django.conf import settings 
import hmac
import hashlib
import base64


def generate_license_key(request):
    # Buscar apenas as chaves de licença ATIVADAS associadas ao usuário logado
    licenses = LicenseKey.objects.filter(user=request.user, status='ATIVADO').order_by('-created_at')
    return render(request, 'licencas/generate_license.html', {'licenses': licenses})



# Função para validar a chave de licença
def is_valid_license_key(license_key, expiration_date):
    secret_key = settings.LICENSE_SECRET_KEY  # Segredo armazenado em settings.py

    # Gere o HMAC com a data de expiração recebida
    generated_signature = hmac.new(
        secret_key.encode(),
        expiration_date.encode(),
        hashlib.sha256
    ).digest()

    # Codifique a assinatura gerada em Base64 URL-safe
    expected_key = base64.urlsafe_b64encode(generated_signature).decode('utf-8').rstrip("=")

    # Formate a chave gerada para comparações (em blocos de 4 caracteres)
    formatted_key = "-".join([expected_key[i:i+4] for i in range(0, len(expected_key), 4)]).upper()

    # Depuração: Verifique se as chaves gerada e fornecida são iguais
    print(f"Formatted Key (Python): {formatted_key}")
    print(f"License Key (Received): {license_key}")

    # Verifique se a chave fornecida corresponde à chave formatada
    return license_key == formatted_key

# View para adicionar a chave de licença
def add_license_key(request):
    if request.method == 'POST':
        license_key = request.POST.get('license_key')
        expiration_date = request.POST.get('expiration_date')  # Recebe a data de expiração enviada pelo frontend

        # Depuração: Verifique a data recebida
        print(f"Expiration Date (Received): {expiration_date}")

        # Verificar se a chave já foi utilizada
        if LicenseKey.objects.filter(key=license_key).exists():
            messages.error(request, "Essa chave de acesso já foi utilizada!")
            return redirect('generate_license_key')

        # Validação da chave gerada
        if not expiration_date or not is_valid_license_key(license_key, expiration_date):
            messages.error(request, "Chave de acesso inválida!")
            return redirect('generate_license_key')

        # Expire todas as chaves anteriores do usuário
        LicenseKey.objects.filter(user=request.user, status='ATIVADO').update(status='VENCIDA')

        # Criar e salvar a nova chave com status "ATIVADO"
        LicenseKey.objects.create(
            key=license_key,
            status='ATIVADO',
            expiration_date=expiration_date,  # Aqui você usa a data recebida
            created_at=timezone.now(),
            user=request.user,  # Atribui automaticamente o usuário logado
        )

        messages.success(request, "Chave ativada com sucesso!")
        return redirect('generate_license_key')

    # Renderize a página de geração de licença
    return render(request, 'licencas/generate_license.html')
   