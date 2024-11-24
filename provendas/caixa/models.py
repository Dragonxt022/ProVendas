# caixa/models.py

from django.db import models
from django.contrib.auth.models import User  # para relacionar com o vendedor
from clientes.models import Cliente  # relacionamento com Cliente
from estoque.models import Produto


class CaixaPdv(models.Model):
    STATUS_CHOICES = [
        ('Rascunho', 'Rascunho'),
        ('Finalizado', 'Finalizado'),
        ('Em aberto', 'Em aberto'),
    ]
    
    caixa = models.ForeignKey('Caixa', on_delete=models.CASCADE, null=True, blank=True)
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
    
    
class Caixa(models.Model):
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Fechado', 'Fechado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aberto')
    aberto_em = models.DateTimeField(auto_now_add=True)
    fechado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Caixa #{self.id} - {self.status}"
    
class OperacaoCaixa(models.Model):
    OPERACAO_CHOICES = [
        ('adicionar', 'Adicionar'),
        ('retirar', 'Retirar'),
    ]

    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    operacao = models.CharField(max_length=10, choices=OPERACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operacao.capitalize()} - R${self.valor} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"
