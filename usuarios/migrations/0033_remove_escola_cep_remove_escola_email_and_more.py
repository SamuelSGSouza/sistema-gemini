# Generated by Django 4.2.9 on 2024-04-16 01:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0032_remove_aluno_escola_remove_escola_coordenador_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='escola',
            name='cep',
        ),
        migrations.RemoveField(
            model_name='escola',
            name='email',
        ),
        migrations.RemoveField(
            model_name='escola',
            name='endereco',
        ),
        migrations.RemoveField(
            model_name='escola',
            name='numero',
        ),
        migrations.RemoveField(
            model_name='escola',
            name='telefone',
        ),
    ]
