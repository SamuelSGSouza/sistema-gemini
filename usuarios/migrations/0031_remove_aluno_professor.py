# Generated by Django 4.0 on 2024-04-14 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0030_remove_turma_alunos_aluno_turma'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aluno',
            name='professor',
        ),
    ]
