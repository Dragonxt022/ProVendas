# Generated by Django 5.1.2 on 2024-10-31 20:25

import django.db.models.deletion
import provendas.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('codigo_barras', models.CharField(blank=True, max_length=50, null=True)),
                ('tipo_cadastro', models.CharField(choices=[('simples', 'Produto Simples'), ('multiplo', 'Produto com Múltiplos Valores'), ('promocional', 'Produto Promocional'), ('validade', 'Produto com Data de Validade')], default='simples', max_length=20)),
                ('preco_venda', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('preco_custo', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('quantidade_estoque', models.IntegerField(blank=True, null=True)),
                ('file', models.ImageField(blank=True, null=True, upload_to=provendas.utils.caminho_upload)),
                ('status', models.CharField(choices=[('ativado', 'Ativado'), ('desativado', 'Desativado')], default='ativado', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('variavel_nome', models.CharField(blank=True, max_length=255, null=True)),
                ('variavel_preco_venda', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('variavel_preco_custo', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('preco_promocional', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('data_expiracao', models.DateField(blank=True, null=True)),
                ('data_validade', models.DateField(blank=True, null=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='estoque.categoriaproduto')),
            ],
        ),
    ]
