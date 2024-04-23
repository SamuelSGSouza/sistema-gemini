# Generated by Django 4.2.2 on 2023-07-04 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0010_alter_questao_habilidades_abncc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questao',
            name='habilidades_abncc',
            field=models.ManyToManyField(blank=True, to='simulados.habilidadesbncc', verbose_name='Habilidades da BNCC'),
        ),
        migrations.AlterField(
            model_name='questao',
            name='nivel_proficiencia',
            field=models.ManyToManyField(blank=True, to='simulados.nivelproficiencia', verbose_name='Nível de proficiência'),
        ),
    ]
