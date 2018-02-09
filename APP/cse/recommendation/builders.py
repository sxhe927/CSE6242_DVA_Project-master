import nltk,json,numpy,math
import numpy as np
from nltk.stem.wordnet import WordNetLemmatizer
from .models import Ingredient, Essence, Recipe, PMI, Compound
nltk.download('wordnet')
lmtzr = WordNetLemmatizer()
from django.db.models import Q


SYNONYMS={
    'beef':['steak','sirloin','ox'],
    'fish':['herring','catfish','anchovy','bass','trout','shark','eel','tilapia','haddock','monkfish','flounder'],
    'starch':['noodle','pasta','flour','bun','roll','cake','dough','craker','wrap'],
    'cow':['ox'],
    'meat':['beef','steak','boar','deer','elk','rabbit','duck','hot dog','venison'],
    'sausage':['hot dog'],
    'shellfish':['clam','mussel','lobser','crab'],
    'corn':['maize']
}

######### Database initialization helpers #########
def match_ingredient_essence():
    for ingre in Ingredient.objects.all():
        names = ' '.join([ lmtzr.lemmatize(x.strip()) for x in ' '.join(json.loads(ingre.name)).lower().split(' ')])
        names = ' '+ names + ' '
        for e in Essence.objects.all():
            if ' '+e.name+' ' in names:
                ingre.essence.add(e)
        for ename,syns in SYNONYMS.iteritems():
            for syn in syns:
                if ' '+syn+' ' in names:
                    ingre.essence.add(Essence.objects.get(name=ename))
        ingre.save()

def categorize_essence(f):
    content = f.readlines()
    content = [x.strip().split(',') for x in content]
    for line in content:
        try:
            essence = Essence.objects.get(name = line[0])
            if line[1] == 'X':
                essence.delete()
            else:
                essence.ingre_type = line[1]
                essence.save()
        except Essence.DoesNotExist:
            pass

def match_essence_compound():
    for compound in Compound.objects.all():
        keywords = [x.encode('utf-8') for x in  json.loads(compound.natural_occ)]
        for word in keywords:
            for essence in Essence.objects.all():
                if essence.name.encode('utf-8') in word:
                    essence.compounds.add(compound)

def match_recipe_ingredient():
    for recipe in Recipe.objects.filter(ingredients__isnull = True):
        ingredients = json.loads(recipe.ingred_list)
        qstr = '|'.join(['Q(id='+str(x)+')' for x in ingredients])
        if qstr != '':
            q = eval(qstr)
            recipe.ingredients.add(*[x for x in Ingredient.objects.filter(q)])
        recipe.save()


def populate_pmi():
    print 'building matrix'
    recipes = Recipe.objects.filter(dish_types__icontains = 'main dish')
    ingredient_idx_list = [o.id for o in Ingredient.objects.all()]
    ingredient_list = list(Ingredient.objects.all())
    N = len(recipes)
    m = len(ingredient_list)
    occur_m = np.zeros((N,m))

    for i, recipe in enumerate(recipes):
      for ingredient in json.loads(recipe.ingred_list):
        occur_m[i, ingredient_idx_list.index(ingredient)] = 1
    cooccur_freq = np.dot(occur_m.T, occur_m)
    pmis = []
    newPMIOs = []
    print 'creating pmis'
    for id1 in range(m):
        for id2 in range(m):
            cooccurrence = cooccur_freq[id1, id2]
            if cooccurrence != 0 and id1 != id2:
                pmi = math.log10( float(N) * cooccurrence /cooccur_freq[id1, id1]/cooccur_freq[id2,id2])
                cond_prob = float(cooccurrence)/cooccur_freq[id1, id1]
                co_occ = cooccurrence
                pmis.append((id1,id2,pmi,cond_prob,co_occ))
    print 'creating PMI Objects'
    for t in set(pmis):
        newPMIOs.append(PMI(ingred1 = ingredient_list[t[0]],
                            ingred2 = ingredient_list[t[1]],
                            pmi = t[2],
                            cond_prob = t[3],
                            co_occ = t[4]))
    print 'dumping PMI Objects'
    PMI.objects.bulk_create(newPMIOs)

def populate_freq():
    for ingredient in Ingredient.objects.all():
        freq = ingredient.pmi.all().count()
        ingredient.freq = freq
        ingredient.save()

######### App Helpers #########
def get_ingred_id_list():
    l = []
    for ingred in Ingredient.objects.all():
        for name in json.loads(ingred.name):
            l.append((name,ingred.id))
    l.sort(key = lambda x: x[0].lower())
    return l


def get_essence_net():
    graph = []
    for i1,e1 in enumerate(Essence.objects.all()):
        for i2,e2 in enumerate(Essence.objects.all()):
            if i1>i2:
                compound1 = set(e1.compounds.all())
                compound2 = set(e2.compounds.all())
                w = len(compound1.intersection(compound2))
                if w>0:
                    graph.append({'source':e1.name, 'target':e2.name, 'value':w})
        print i1
    return graph

def get_essence_freq():
    freq = {}
    for e in Essence.objects.all():
        f = 0
        ingredients = Ingredient.objects.filter(essence__in=[e])
        for i in ingredients:
            f += i.freq
        freq[e.name]=f
    return freq

### n is number of recommended items
def get_recommendation(source_id, aisle , n=8):
    result = []
    essence_list = []
    source = Ingredient.objects.get(id = source_id)
    num = 0
    cond_prob = 0.1
    while num < 2 and cond_prob > -0.3:
        targets = PMI.objects \
                        .filter(ingred1_id = source_id) \
                        .filter(cond_prob__gt=cond_prob) \
                        .filter(ingred2__freq__gte = 0) \
                        .filter(ingred2__essence__ingre_type__in = [aisle]) \
                        .order_by('-pmi').distinct()
        num = len(targets)
        cond_prob -= 0.05
    s_compounds = set(reduce(lambda a,b: a+b, [list(e.compounds.all()) for e in source.essence.all()]))
    for t in [(o.ingred2,o.pmi) for o in targets[:n]]:
        t_compounds = set(reduce(lambda a,b: a+b, [list(e.compounds.all()) for e in t[0].essence.all()]))
        essence_list += list(t[0].essence.all())
        result.append({'name':json.loads(t[0].name)[0],
                       'id': json.loads(t[0].name)[0].replace(' ','-')+'-'+str(t[0].id), 
                       'pmi':"%.2f"%t[1],
                       'compounds':t_compounds.intersection(s_compounds),
                       'essence':','.join([x.name for x in t[0].essence.all()]),
                       })
    essence_list = list(set([x.name for x in essence_list]))
    return result,essence_list

