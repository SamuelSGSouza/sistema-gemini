# Generated by Django 4.2.9 on 2024-05-06 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0044_remove_simulado_componente_questao_componente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questaoreferencia',
            name='quantidade_respostas_a',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Quantidade de respostas A'),
        ),
        migrations.AlterField(
            model_name='questaoreferencia',
            name='quantidade_respostas_b',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Quantidade de respostas B'),
        ),
        migrations.AlterField(
            model_name='questaoreferencia',
            name='quantidade_respostas_c',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Quantidade de respostas C'),
        ),
        migrations.AlterField(
            model_name='questaoreferencia',
            name='quantidade_respostas_d',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Quantidade de respostas D'),
        ),
    ]