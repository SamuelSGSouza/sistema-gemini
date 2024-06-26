# Generated by Django 4.2.2 on 2023-08-14 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0025_alter_coordenador_cpf_alter_coordenadorgeral_cpf_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordenador',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF (somente números)'),
        ),
        migrations.AlterField(
            model_name='coordenador',
            name='telefone',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AlterField(
            model_name='coordenadorgeral',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF (somente números)'),
        ),
        migrations.AlterField(
            model_name='coordenadorgeral',
            name='telefone',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AlterField(
            model_name='professor',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF (somente números)'),
        ),
        migrations.AlterField(
            model_name='professor',
            name='telefone',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AlterField(
            model_name='secretario',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF (somente números)'),
        ),
        migrations.AlterField(
            model_name='secretario',
            name='telefone',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
    ]
