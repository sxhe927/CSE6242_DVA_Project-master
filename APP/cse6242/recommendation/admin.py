# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import File,Ingredient,Recipe,Compound,Essence,PMI
# Register your models here.

class PMIInline(admin.TabularInline):
    model= Ingredient.pmi.through
    fk_name = "ingred2"

@admin.register(Essence)
class EssenceAdmin(admin.ModelAdmin):
    filter_horizontal = ('compounds',)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass

@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    #inlines = (PMIInline,)
    filter_horizontal = ('essence',)
    

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('ingredients',)


@admin.register(PMI)
class PMIAdmin(admin.ModelAdmin):
    pass