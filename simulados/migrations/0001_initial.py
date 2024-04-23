# Generated by Django 4.2.2 on 2023-06-30 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Questao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matriz_referencial', models.CharField(choices=[('matematica', 'Matemática'), ('portugues', 'Português')], default='matematica', max_length=255, verbose_name='Matriz Referencial')),
                ('descritor', models.CharField(max_length=255, verbose_name='Descritor')),
                ('ano', models.IntegerField(verbose_name='Ano')),
                ('habilidades_abncc', models.CharField(max_length=255, verbose_name='Habilidades da BNCC')),
                ('nivel_proficiencia', models.IntegerField(verbose_name='Nível de Proficiência')),
                ('enunciado', models.TextField(verbose_name='Enunciado')),
                ('alternativa_a', models.CharField(max_length=255, verbose_name='Alternativa A')),
                ('alternativa_b', models.CharField(max_length=255, verbose_name='Alternativa B')),
                ('alternativa_c', models.CharField(max_length=255, verbose_name='Alternativa C')),
                ('alternativa_d', models.CharField(max_length=255, verbose_name='Alternativa D')),
                ('alternativa_correta', models.CharField(choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')], max_length=255, verbose_name='Resposta')),
                ('suporte_texto', models.TextField(verbose_name='Suporte de Texto')),
                ('suporte_imagem', models.ImageField(upload_to='suporte_imagem', verbose_name='Suporte de Imagem')),
            ],
        ),
        migrations.CreateModel(
            name='QuestaoReferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_questao', models.IntegerField(verbose_name='Número da questão')),
                ('questao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulados.questao', verbose_name='Questão')),
            ],
        ),
        migrations.CreateModel(
            name='Simulado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome do simulado')),
                ('questoes_referencia', models.ManyToManyField(to='simulados.questaoreferencia', verbose_name='Questões de referência')),
            ],
        ),
        migrations.CreateModel(
            name='Resposta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_respostas_a', models.IntegerField(verbose_name='Quantidade de respostas A')),
                ('quantidade_respostas_b', models.IntegerField(verbose_name='Quantidade de respostas B')),
                ('quantidade_respostas_c', models.IntegerField(verbose_name='Quantidade de respostas C')),
                ('quantidade_respostas_d', models.IntegerField(verbose_name='Quantidade de respostas D')),
                ('quantidade_respostas_corretas', models.IntegerField(verbose_name='Quantidade de respostas corretas')),
                ('questao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulados.questao')),
                ('simulado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulados.simulado')),
            ],
        ),
    ]
