# Generated by Django 4.2.2 on 2023-08-03 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0015_escola_secretario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escola',
            name='secretario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.secretario'),
        ),
    ]
