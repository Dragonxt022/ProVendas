# models.py
from django.db import models
from provendas.utils import caminho_upload

class Configuracao(models.Model):
    nome_aplicacao = models.CharField(max_length=100)
    cliente_padrao = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    cor_primaria = models.CharField(max_length=7, default="#000000")
    cor_secundaria = models.CharField(max_length=7, default="#FFFFFF")
    logo_empresa = models.ImageField(upload_to=caminho_upload, null=True, blank=True)
    icone_aplicacao = models.ImageField(upload_to=caminho_upload, null=True, blank=True)  # Novo campo para o ícone

    def __str__(self):
        return self.nome_aplicacao
