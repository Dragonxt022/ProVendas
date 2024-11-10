# Generated by Django 5.1.2 on 2024-11-07 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_cliente_limite_credito_cliente_limite_credito_ativo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='limite_credito',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='limite_credito_ativo',
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cep',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
