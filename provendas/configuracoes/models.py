from django.db import models

class Configuracao(models.Model):
    nome_aplicacao = models.CharField(max_length=255, null=True, blank=True)
    cor_principal = models.CharField(max_length=7, null=True, blank=True)  # Cor principal no formato HEX, ex: #FF5733
    cliente_padrao = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return "Configurações Gerais"
