# Generated by Django 5.1.2 on 2024-11-13 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='caixapdv',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
