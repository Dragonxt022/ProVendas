# Generated by Django 5.1.2 on 2024-11-13 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licencas', '0006_licensekey_system_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='licensekey',
            name='unique_key_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
