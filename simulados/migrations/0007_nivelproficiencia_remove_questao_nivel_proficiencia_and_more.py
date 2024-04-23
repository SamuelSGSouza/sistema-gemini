# Generated by Django 4.2.2 on 2023-07-04 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0006_alter_descritor_options_remove_questao_descritor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NivelProficiencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.CharField(max_length=255, verbose_name='Nível de proficiência')),
            ],
        ),
        migrations.RemoveField(
            model_name='questao',
            name='nivel_proficiencia',
        ),
        migrations.AddField(
            model_name='questao',
            name='nivel_proficiencia',
            field=models.ManyToManyField(to='simulados.nivelproficiencia', verbose_name='Nível de proficiência'),
        ),
    ]
