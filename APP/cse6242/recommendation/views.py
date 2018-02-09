# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import loader, RequestContext
from .forms import FileForm
from .models import File,Essence,Compound,Ingredient,Recipe,INGRE_TYPE_CHOICES
import pickle,json
from .builders import *
import sys
import operator


def recipes(request):
    r_ids_str = request.GET.get('r_ids',0)
    source_id = int(request.GET.get('source_id',0))
    r_ids = [int(x) for x in r_ids_str.split(',')]
    # list of ids in cart
    ingredients = [Ingredient.objects.get(id=x) for x in [source_id]+r_ids]
    count = 0
    recipes = []
    while count == 0:
        recipes = reduce((lambda x,y: x&y), [ingred.assoc_recipes.all() for ingred in ingredients])
        count = len(recipes)
        ingredients = ingredients[:-1]
    ordered = sorted(recipes, key=operator.attrgetter('likes'), reverse=True)
    context = { 'recipes':ordered[:16],
    }

    #render the page
    return render(request,'recipes.html',context)

def app(request):
    source_id_str = request.GET.get('source_id', 0)
    results = []
    graph_nodes = []
    source_essence = []
    if source_id_str != 0:
        source_id = int(source_id_str.split('-')[1])
        for t in INGRE_TYPE_CHOICES:
            re,es = get_recommendation(source_id,t[0])
            results.append({'id':t[0],
                            'name': t[1],
                            'recommendations': re})
            graph_nodes += es
        graph_nodes = list(set(graph_nodes))
        source_essence = json.dumps(list([x.name for x in Ingredient.objects.get(id=source_id).essence.all()]))
    context = { 'results':results,
                'ingred_id_list': json.dumps(get_ingred_id_list()),
                'graph_nodes':json.dumps(graph_nodes),
                'source_essence':source_essence,
                }
    return render(request,'app.html',context)

def index(request):
    template = loader.get_template('base.html')
    context={}
    return HttpResponse(template.render(context, request))


def initialize(request):
    # Handle file upload
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = File(file = request.FILES['file'])

            if 'essence' in request.POST:
                essence = pickle.load(newfile.file)
                for idx,e in enumerate(essence):
                    newEssence = Essence(id = idx, name = e.decode('utf-8') )
                    newEssence.save()
            if 'essence-type' in request.POST:
                categorize_essence(newfile.file)
            if 'compound' in request.POST:
                compound = pickle.load(newfile.file)
                c_idx = compound.keys()
                for idx,c in enumerate(c_idx):
                    newCompound = Compound(id = idx, name = c.strip(), natural_occ = json.dumps(compound[c]['Natural_occ']), cas_no = compound[c]['CAS_No'])
                    newCompound.save()
            if 'ingredient' in request.POST:
                ingredient = pickle.load(newfile.file)
                for idx,names in ingredient.items():
                    newIngre = Ingredient(id = idx, name = json.dumps(names))
                    newIngre.save()
            if 'recipe' in request.POST:
                recipes = json.load(newfile.file)
                for count,recipe in enumerate(recipes):
                    if 'id' in recipe:
                        titile = ''
                        if 'title' in recipe:
                            title = recipe['title']
                        instr = ''
                        if 'instructions' in recipe:
                            instr = recipe['instructions']
                        srcurl = ''
                        if 'spoonacularSourceUrl' in recipe:
                            srcurl = recipe['spoonacularSourceUrl']
                        imgurl = ''
                        if 'image' in recipe:
                            imgurl = recipe['image']
                        ingreds = []
                        if 'ingredients' in recipe:
                            ingreds = recipe['ingredients']
                        types = ''
                        if 'dishTypes' in recipe:
                            types = recipe['dishTypes']
                        likes = 0
                        if 'aggregateLikes' in recipe:
                            likes = int(recipe['aggregateLikes'])
                        newRecipe = Recipe(name = title, likes = likes, id = recipe['id'], source_url = srcurl, image_url = imgurl, ingred_list = json.dumps(ingreds), dish_types = json.dumps(types))
                        newRecipe.save()
                        if count % 50 == 0:
                            sys.stdout.write('\rProgress: %.2f%%' % (float(count)/len(recipes)*100))
                            sys.stdout.flush()
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('initialize'))
        
        if 'essence-reset' in request.POST:
            Essence.objects.all().delete()
        if 'compound-reset' in request.POST:
            Compound.objects.all().delete()
        if 'ingredient-reset' in request.POST:
            Ingredient.objects.all().delete()
        if 'recipe-reset' in request.POST:
            Recipe.objects.all().delete()
        if 'PMI-reset' in request.POST:
            PMI.objects.all().delete()
        if 'match-essence' in request.POST:
            match_ingredient_essence()
        if 'match-ingredient' in request.POST:
            match_recipe_ingredient()
        if 'match-compound' in request.POST:
            match_essence_compound()
        if 'PMI' in request.POST:
            populate_pmi()
        if 'freq' in request.POST:
            populate_freq()
    else:
        form = FileForm() # A empty, unbound form

    # Render list page with the documents and the form
    context = {
                'form':form,
                'essences':Essence.objects.all(),
                'compounds':Compound.objects.all(),
                'ingredients':Ingredient.objects.all(),
                'recipes':Recipe.objects.all(),
    }

    return render (request, 'initialize.html', context)