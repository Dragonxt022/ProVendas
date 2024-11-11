# provendas/utils.py
import os
from datetime import datetime
import hashlib
from django.utils.crypto import get_random_string

def caminho_upload(instance, filename):
    # Obtém o mês e ano atual no formato mm-aaaa
    subpasta = datetime.now().strftime("%m-%Y")
    
    # Limita o comprimento do nome do arquivo a 200 caracteres
    nome_arquivo, extensao = os.path.splitext(filename)
    nome_arquivo = nome_arquivo[:200]  # Trunca para garantir que não ultrapasse 200 caracteres
    
    # Garante que o nome do arquivo seja único, adicionando um hash ou um sufixo aleatório
    nome_arquivo = f"{nome_arquivo}_{get_random_string(8)}"  # Gerando sufixo aleatório para evitar conflitos

    # Retorna o caminho completo, incluindo o nome do arquivo gerado
    return os.path.join("images", subpasta, f"{nome_arquivo}{extensao}")


def converter_para_float(valor):
    """Converte uma string no formato 'R$ 12,00' para um float."""
    return float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())

def converter_para_reais(valor):
    """Converte um float para o formato 'R$ 12,00'."""
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
