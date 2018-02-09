from django import template
from recommendation.models import Essence,Ingredient,Recipe
register = template.Library()

@register.simple_tag
def size(model):
    return len(model)

@register.simple_tag
def essence_coverage():
    percentage = (1-(float(len(Ingredient.objects.filter(essence__isnull = True)))/Ingredient.objects.all().count()))*100
    return '%.2f%%'%percentage

@register.simple_tag
def ingredient_coverage():
    percentage = (1-(float(len(Recipe.objects.filter(ingredients__isnull = True)))/Recipe.objects.all().count()))*100
    return '%.2f%%'%percentage

@register.simple_tag
def compound_coverage():
    percentage = (1-(float(len(Essence.objects.filter(compounds__isnull = True)))/Essence.objects.all().count()))*100
    return '%.2f%%'%percentage

@register.simple_tag
def get_comp_title(complist):
    title = '<br>'.join([x.name for x in complist])
    return title