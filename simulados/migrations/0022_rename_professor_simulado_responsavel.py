# Generated by Django 4.2.2 on 2023-08-07 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0021_alter_simulado_tipo_simulado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simulado',
            old_name='professor',
            new_name='responsavel',
        ),
    ]
