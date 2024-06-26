# Generated by Django 4.2.9 on 2024-05-01 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0041_remove_questao_grau_ensino_simulado_grau_ensino_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questao',
            name='componente',
        ),
        migrations.RemoveField(
            model_name='questao',
            name='matriz_referencial',
        ),
        migrations.AddField(
            model_name='questao',
            name='unidade_tematica_texto',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Unidade Temática'),
        ),
        migrations.AddField(
            model_name='simulado',
            name='componente',
            field=models.CharField(choices=[('Língua Portuguesa', 'Língua Portuguesa'), ('Arte', 'Arte'), ('Educação Física', 'Educação Física'), ('Inglês', 'Inglês'), ('História', 'História'), ('Geografia', 'Geografia'), ('Ensino Religioso', 'Ensino Religioso'), ('Ciências', 'Ciências'), ('Matemática', 'Matemática')], default='Matemática', max_length=255, verbose_name='Componente Curricular'),
        ),
        migrations.AddField(
            model_name='simulado',
            name='matriz_referencial',
            field=models.CharField(choices=[('Matemática', 'Matemática'), ('Humanas', 'Humanas'), ('Linguagens', 'Linguagens'), ('Ciências', 'Ciências')], default='Matemática', max_length=255, verbose_name='Matriz Referencial'),
        ),
    ]
