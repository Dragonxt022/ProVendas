# Generated by Django 5.1.2 on 2024-11-13 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('licencas', '0003_licensekey_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='licensekey',
            name='status',
        ),
    ]