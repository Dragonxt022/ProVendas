from django.db import models
from django.contrib.auth.models import User
from empresas.models import Empresa
from django.utils.text import slugify
from provendas.utils import caminho_upload 

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    file = models.ImageField(upload_to=caminho_upload, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:  # Gera o slug apenas se ele ainda não existir
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    codigo_barras = models.CharField(max_length=50, null=True, blank=True)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE, related_name='produtos')
    preco_de_venda = models.DecimalField(max_digits=8, decimal_places=2)
    preco_de_cursto = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade_estoque = models.IntegerField(null=True, blank=True)
    file = models.ImageField(upload_to=caminho_upload, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('ativado', 'Ativado'), ('desativado', 'Desativado')], default='ativado')
    controle_estoque = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Gera o slug apenas se ele ainda não existir
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            # Garante que o slug seja único
            while Produto.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
