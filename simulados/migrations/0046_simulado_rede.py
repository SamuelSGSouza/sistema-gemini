# Generated by Django 4.2.9 on 2024-06-06 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0045_alter_questaoreferencia_quantidade_respostas_a_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulado',
            name='rede',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Rede'),
        ),
    ]
