# Generated by Django 5.1.6 on 2025-02-17 20:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0005_remove_servico_funcionario_servico_responsaveis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horario',
            name='data_marcada',
        ),
        migrations.AddField(
            model_name='horario',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='horario',
            name='hora',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
