# Generated by Django 4.2.2 on 2023-08-07 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0025_remove_simulado_responsavel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simulado',
            old_name='user_responsavel',
            new_name='responsavel',
        ),
    ]
