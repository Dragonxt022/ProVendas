from django.db import models

class Configuracao(models.Model):
    nome_aplicacao = models.CharField(max_length=100)
    cliente_padrao = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    cor_primaria = models.CharField(max_length=7, default="#ff670f")  # Exemplo de cor no formato hex
    cor_secundaria = models.CharField(max_length=7, default="#ffd30f")
    logo_empresa = models.ImageField(upload_to='logos/', null=True, blank=True)
    
    def __str__(self):
        return "Configurações Gerais"
