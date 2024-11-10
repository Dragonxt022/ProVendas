# provendas/utils.py
import os
from datetime import datetime

def caminho_upload(instance, filename):
    # Obtém o mês e ano atual no formato mm-aaaa
    subpasta = datetime.now().strftime("%m-%Y")
    # Define o caminho completo
    return os.path.join("images", subpasta, filename)


def converter_para_float(valor):
    """Converte uma string no formato 'R$ 12,00' para um float."""
    return float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())

def converter_para_reais(valor):
    """Converte um float para o formato 'R$ 12,00'."""
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
