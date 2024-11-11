# Generated by Django 5.1.2 on 2024-11-01 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0007_remove_produto_data_validade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='tipo_cadastro',
            field=models.CharField(choices=[('simples', 'Produto Simples'), ('multiplo', 'Produto com Múltiplos Valores')], default='simples', max_length=20),
        ),
    ]