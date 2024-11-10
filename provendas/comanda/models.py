from django.db import models
from django.contrib.auth.models import User  # Para relacionar com o vendedor
from estoque.models import Produto  # Para referenciar o modelo Produto

class Mesa(models.Model):
    STATUS_CHOICES = [
        ('livre', 'Livre'),
        ('ocupada', 'Ocupada'),
    ]
    
    nome = models.CharField(max_length=100)  # Nome ou número da mesa
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='livre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mesa {self.nome} - {self.status}"

class Comanda(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
    ]
    
    numero_pedido = models.CharField(max_length=100, unique=True)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aberta')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='N/D')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, null=True, blank=True)  # Relacionamento com Cliente
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'  # Define o campo usado para determinar a última comanda

    def __str__(self):
        return f"Comanda #{self.id} - {self.status}"

class ProdutoComanda(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} (Comanda #{self.comanda.id})"
