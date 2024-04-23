# Generated by Django 4.0 on 2024-04-14 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0028_remove_aluno_turma_remove_escola_turmas_turma_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='escola',
            name='turmas_escola',
        ),
        migrations.AddField(
            model_name='turma',
            name='escola',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuarios.escola'),
            preserve_default=False,
        ),
    ]
