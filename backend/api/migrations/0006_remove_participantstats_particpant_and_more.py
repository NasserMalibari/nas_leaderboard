# Generated by Django 5.1.6 on 2025-02-23 12:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_rename_particpantstats_participantstats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participantstats',
            name='particpant',
        ),
        migrations.AlterField(
            model_name='participantstats',
            name='id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='api.participant'),
        ),
    ]
