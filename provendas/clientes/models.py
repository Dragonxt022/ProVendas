from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=255, unique=True)
    telefone = models.CharField(max_length=255, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')], default='ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.nome
