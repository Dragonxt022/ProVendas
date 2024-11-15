from django.db import models
from django.utils import timezone


class LicenseKey(models.Model):
    STATUS_CHOICES = [
        ('ATIVADO', 'Ativado'),
        ('VENCIDA', 'Vencida'),
    ]
    
    key = models.CharField(max_length=500, unique=True)  # Chave da licença
    expiration_date = models.DateTimeField()  # Data de validade
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação da chave
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VENCIDA')  # Status da chave

    def is_valid(self):
        """Verifica se a chave ainda é válida"""
        return self.status == 'ATIVADO' and self.expiration_date > timezone.now()

    def days_remaining(self):
        """Calcula os dias restantes até o vencimento"""
        if self.status == 'ATIVADO' and self.expiration_date > timezone.now():
            return (self.expiration_date - timezone.now()).days
        return 0  # Se a chave já está vencida ou não ativada

    def __str__(self):
        return self.key
