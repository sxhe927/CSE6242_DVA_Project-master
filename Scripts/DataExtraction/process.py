import os, json, pickle
import numpy as np
import os.path
from tempfile import TemporaryFile
import math, random

# load all recipes
print('Loading all recipes ...')
files = [x for x in os.listdir('../DataExtraction/Recipes') if x.endswith(".txt")]
allrecipes = []
for fname in files:
    with open('../DataExtraction/Recipes/'+fname, 'r') as f:
        for line in f:
            allrecipes.append(json.loads(line))
print(str(len(allrecipes)) + ' recipes loaded.')

# Load ingredients to a dictionary
if not os.path.isfile('ingredient_dict'):
    print('ingredient_dict not found, building one from all recipes ...')
    ingredients = set(list(map(lambda x: (x['id'],x['name'],x['aisle']),
        filter(lambda x: 'id' in x and 'name' in x and 'aisle' in x,
            reduce(lambda x,y: x+y, 
                list(map(lambda x: x['extendedIngredients'],
                    list(filter(lambda x: 'extendedIngredients' in x,
                        allrecipes)))))))))

    ingredient_dict = {}
    for t in ingredients:
        ingredient_id = t[0]
        ingredient_name = t[1]
        if ingredient_id in ingredient_dict:
            ingredient_dict[ingredient_id].append(ingredient_name)
        else:
            ingredient_dict[ingredient_id] = [ingredient_name]

    ###Save List###
    print('Saved '+str(len(ingredient_dict))+' ingredients to file ingredients_dict')
    with open("ingredient_dict", "wb") as fp:   #Pickling
        pickle.dump(ingredient_dict, fp)
else:
    with open(r"ingredient_dict", "rb") as input_file:
        ingredient_dict = pickle.load(input_file)
    print('Found existing ingredient_dict, loaded '+ str(len(ingredient_dict))+' ingredients.')


#Build Cooccurrence Matrix
print('Building cooccurrence matrix ...')

# filter recipes based on dish types
recipes = filter(lambda x: 'main dish' in x['dishTypes'],filter(lambda x: 'dishTypes' in x, allrecipes))

#Get ingredient occurrences
print('Loading ingredients occurrences among recipes ...')
ingredient_occur = map(lambda x: map(lambda i: i['id'], filter(lambda obj : 'id' in obj, x)), 
            list(map(lambda x: x['extendedIngredients'],
                list(filter(lambda x: 'extendedIngredients' in x,
                    recipes)))))

ingredient_list = list(ingredient_dict.keys())
N = len(ingredient_occur)
m = len(ingredient_list)

occur_m = np.zeros((N,m))

for i, recipe in enumerate(ingredient_occur):
  for ingredient in recipe:
    occur_m[i, ingredient_list.index(ingredient)] = 1
    

# Save Matrix
np.save('occur_m', occur_m)
print('Matrix saved to file occur_m.npy')


## Build Network Visualization
print('Generating network ...')
if not os.path.exists('network'):
    os.makedirs('network')

cooccur_freq = np.dot(occur_m.T, occur_m)
with open("network/ingredient_net.csv", "w") as output:
  output.write('Target,Source,Weight\n')
  for id1 in range(m):
    for id2 in range(m):
      cooccurrence = cooccur_freq[id1, id2]
      if id1 < id2 and cooccurrence != 0:
        PMI = math.log10( N * cooccurrence /cooccur_freq[id1, id1]/cooccur_freq[id2,id2])
        line = str(ingredient_list[id1]) + ',' + str(ingredient_list[id2]) + ',' + str(PMI) + '\n'
        output.write(line)

###Get Ingredient Labels###
with open("network/ingredient_labels.csv", "w") as output:
    output.write("Id,Label\n")
    for k in ingredient_dict.keys():
        output.write(str(k)+","+ingredient_dict[k][0].encode('utf-8')+"\n")
print('Network saved to netwok.')


###Ingredient Distribution###
ingredient_distr = []
ingredient_distr_dict = {}
for idx, v in enumerate(np.diag(cooccur_freq)):
    ingredient_distr.append([ingredient_list[idx],ingredient_dict[ingredient_list[idx]],v])
    ingredient_distr_dict[ingredient_list[idx]] = v

ingredient_distr.sort(key=lambda x: x[2])

with open('ingredient_distr','wb') as fp:
    pickle.dump(ingredient_distr_dict, fp)
# for v in ingredient_distr:
#         print ([v[2],v[1][0]])
print('Ingredient distribution saved to file ingredient_distr.')

#save all recipes
for recipe in allrecipes:
    if 'extendedIngredients' in recipe:
        ingredients = [x['id'] for x in filter(lambda x: 'id' in x , [x for x in recipe['extendedIngredients']])]
        removed = recipe.pop('extendedIngredients',None)
        recipe['ingredients'] = ingredients

with open('recipe_dump','wb') as fp:
    json.dump(allrecipes, fp)

print('All recipes dumped to file recipe_dump.')

recipes_min = [allrecipes[i] for i in random.sample(xrange(len(allrecipes)), 2500)]
with open('recipe_dump_min','wb') as fp:
    json.dump(recipes_min, fp)

print('Randomly sampled 2500 recipes dumped to file recipe_dump_min.')



    