# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import json
# Create your models here.
INGRE_TYPE_CHOICES = (
                        ('M','Meat'),
                        ('V','Vegetable'),
                        ('F','Fruit'),
                        ('SE','Seafood'),
                        ('D','Dairy'),
                        ('N','Nuts'),
                        ('G','Grains'),
                        ('SP','Spice'),
                        ('A','Alcohol'),
                        ('O','Other'),

)


class Compound(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    cas_no = models.CharField(max_length=30)
    natural_occ = models.TextField(default='')
    def __unicode__(self):
        return self.name

class Essence(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    compounds = models.ManyToManyField(Compound)
    ingre_type = models.CharField(max_length=20, choices = INGRE_TYPE_CHOICES, default = 'O')
    
    def __unicode__(self):
        return self.name

class Ingredient(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    essence = models.ManyToManyField(Essence)
    image = models.CharField(max_length=100)
    pmi = models.ManyToManyField('self', through='PMI', symmetrical = False, through_fields = ('ingred1','ingred2'))
    freq = models.IntegerField(default=0)
    def __unicode__(self):
        return ', '.join(json.loads(self.name))

class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    source_url = models.CharField(max_length=100, default = '')
    likes = models.IntegerField(default=0)
    image_url = models.CharField(max_length=100, default='')
    dish_types = models.CharField(max_length=100, default='')
    ingred_list = models.CharField(max_length=100, default = '')
    ingredients = models.ManyToManyField(Ingredient, related_name='assoc_recipes')
    def __unicode__(self):
        return self.name

class PMI(models.Model):
    ingred1 = models.ForeignKey('Ingredient', related_name='PMI_ingred1', on_delete=models.CASCADE, null=True)
    ingred2 = models.ForeignKey('Ingredient', related_name='PMI_ingred2', on_delete=models.CASCADE, null=True)
    pmi = models.FloatField(default=0)
    cond_prob = models.FloatField(default=0)
    co_occ = models.FloatField(default=0)
class File(models.Model):
    file = models.FileField(upload_to='files/')





    



