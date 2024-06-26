# Generated by Django 4.2.9 on 2024-05-01 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0040_questao_componente_questao_grau_ensino_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questao',
            name='grau_ensino',
        ),
        migrations.AddField(
            model_name='simulado',
            name='grau_ensino',
            field=models.CharField(choices=[('1', '1º ano'), ('2', '2º ano'), ('3', '3º ano'), ('4', '4º ano'), ('5', '5º ano'), ('6', '6º ano'), ('7', '7º ano'), ('8', '8º ano'), ('9', '9º ano'), ('10', '1º ano do Ensino Médio'), ('11', '2º ano do Ensino Médio'), ('12', '3º ano do Ensino Médio')], default='1', max_length=255, verbose_name='Grau de Ensino'),
        ),
        migrations.AlterField(
            model_name='simulado',
            name='nome',
            field=models.CharField(max_length=255, verbose_name='Nome de Avaliação'),
        ),
        migrations.AlterField(
            model_name='simulado',
            name='tipo_simulado',
            field=models.CharField(blank=True, choices=[('questoes_construidas', 'Avaliação Construído'), ('questoes_cadastradas', 'Avaliação Cadastrado'), ('questoes_proficiencia', 'Avaliação Proficiência'), ('questoes_gerais', 'Avaliação Geral')], max_length=255, null=True, verbose_name='Tipo de Avaliação'),
        ),
    ]
