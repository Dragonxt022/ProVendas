# caixa/models.py

from django.db import models
from django.contrib.auth.models import User  # para relacionar com o vendedor
from clientes.models import Cliente  # relacionamento com Cliente
from estoque.models import Produto  # Para referenciar o modelo Produto


class CaixaPdv(models.Model):
    STATUS_CHOICES = [
        ('Rascunho', 'Rascunho'),
        ('Finalizado', 'Finalizado'),
        ('Em aberto', 'Em aberto'),
    ]
    
    numero_pedido = models.CharField(max_length=100, unique=True)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    desconto = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Finalizado')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='N/D')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.status}"


class ProdutoCaixaPdv(models.Model):
    caixa_pdv = models.ForeignKey('CaixaPdv', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} (Venda #{self.caixa_pdv.numero_pedido})"