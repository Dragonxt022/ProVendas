from django.db import models
from provendas.utils import caminho_upload


class Configuracao(models.Model):
    nome_aplicacao = models.CharField(max_length=100)
    cliente_padrao = models.ForeignKey(
        'clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True
    )
    cor_primaria = models.CharField(max_length=7, default="#16bb6e")
    cor_secundaria = models.CharField(max_length=7, default="#09ec41")  
    logo_empresa = models.ImageField(upload_to=caminho_upload, null=True, blank=True)
    icone_aplicacao = models.ImageField(upload_to=caminho_upload, null=True, blank=True)
    gerar_codigo_barra_automatico = models.BooleanField(default=False)
    gerenciar_abertura_fechamento_caixa = models.BooleanField(default=False)

    def __str__(self):
        return self.nome_aplicacao
