# Generated by Django 4.2.2 on 2023-08-07 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0024_simulado_user_responsavel_alter_simulado_responsavel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulado',
            name='responsavel',
        ),
    ]
