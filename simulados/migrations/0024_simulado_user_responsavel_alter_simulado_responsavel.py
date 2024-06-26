# Generated by Django 4.2.2 on 2023-08-07 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usuarios', '0021_remove_coordenador_nome_remove_coordenador_senha_and_more'),
        ('simulados', '0023_alter_simulado_responsavel'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulado',
            name='user_responsavel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='simulado',
            name='responsavel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuarios.professor', verbose_name='Professor'),
            preserve_default=False,
        ),
    ]
