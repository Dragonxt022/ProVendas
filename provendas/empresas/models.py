from django.db import models

class Empresa(models.Model):
    ESTADOS_BRASIL = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ]

    nome_empresa = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')], default='ativo')
    cnpj = models.CharField(max_length=14, unique=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    estado = models.CharField(max_length=2, choices=ESTADOS_BRASIL, null=True, blank=True)  # Corrigido
    endereco = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_empresa
