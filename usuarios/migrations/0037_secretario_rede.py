# Generated by Django 4.2.9 on 2024-06-06 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0036_alter_coordenador_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='secretario',
            name='rede',
            field=models.CharField(default=1, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]