# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendation', '0003_auto_20171127_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='spoonacularID',
        ),
        migrations.AlterField(
            model_name='essence',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
