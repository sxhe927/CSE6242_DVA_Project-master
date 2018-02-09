# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 02:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aisle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('cas_no', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Essence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('compounds', models.ManyToManyField(to='recommendation.Compound')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacularID', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('image', models.CharField(max_length=100)),
                ('aisle', models.ManyToManyField(to='recommendation.Aisle')),
                ('essence', models.ManyToManyField(to='recommendation.Essence')),
            ],
        ),
        migrations.CreateModel(
            name='PMI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pmi', models.FloatField()),
                ('ingredient1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PMI_ingredient1', to='recommendation.Ingredient')),
                ('ingredient2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PMI_ingredient2', to='recommendation.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacularID', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=30)),
                ('instruction', models.CharField(max_length=1000)),
                ('image', models.CharField(max_length=100)),
                ('ingredients', models.ManyToManyField(to='recommendation.Ingredient')),
            ],
        ),
    ]
