# Generated by Django 5.1.2 on 2024-11-15 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('licencas', '0013_alter_licensekey_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LicenseKeyValidation',
        ),
        migrations.RemoveField(
            model_name='licensekey',
            name='user',
        ),
    ]
