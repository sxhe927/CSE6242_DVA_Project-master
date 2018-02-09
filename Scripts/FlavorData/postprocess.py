import pickle, nltk, re
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('stopwords')
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

nltk.download('wordnet')
lmtzr = WordNetLemmatizer()


###load manually processed essence_manual and perform secondary machine cleaning
print('Loading manually processed essence data ...')
with open('essence_manual.txt', 'rb') as file:
    content = file.readlines()

essence = [x.strip() for x in content]
cook_verbs = [('roast','roasted'),('smoke','smoked'),('cook','cooked'),('boil','boiled'),('grill','grilled'),('fry','fried'),('raw','raw')]

for t in cook_verbs:
    essence = [x.replace(t[1]+' ',t[0]+' ') for x in essence]

for i,v in enumerate(essence):
    for t in cook_verbs:
        if t[0] in v and ',' not in v:
            essence[i] = v.replace(t[0]+' ','').strip() + ',' + t[0]
#Ignore cook verbs!
for i,v in enumerate(essence):
    if ',' in v:
        essence[i] = v.split(',')[0].strip()


essence = list(set(essence))
essence.sort()

print('Saved essence to file essence.')
with open('essence', 'wb') as output:
	pickle.dump(essence, output)


###load flavor dictionary
with open('flavor_dict', 'r') as infile:
    flavor_dict = pickle.load(infile)

###load ingredient dictionary
with open('../DataExtraction/ingredient_dict', 'r') as infile:
    ingredient_dict = pickle.load(infile)

### Build Essence Data
essence_dict = {}

flavor_idx = flavor_dict.keys()


for k,v in flavor_dict.iteritems():
    keywords = [x.encode('utf-8') for x in  v['Natural_occ']]
    for word in keywords:
        for e in essence:
            base_e = e.split(',')[0]
            if base_e in word:
                if e in essence_dict:
                    essence_dict[e].append(flavor_idx.index(k))
                else:
                    essence_dict[e] = [flavor_idx.index(k)]

with open('essence_dict', 'wb') as output:
    pickle.dump(essence_dict,output)

print('Essence-->Chemical Compound data saved to essence_dict.')

### Match ingredients to essence
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

ingredient_essence = {}
for k,ingre_names in ingredient_dict.iteritems():
    es = []
    names = ' '.join([ lmtzr.lemmatize(x.strip()) for x in ' '.join(ingre_names).lower().split(' ')])
    names = ' '+ names + ' '
    for idx,e in enumerate(essence):
        if ' '+e+' ' in names:
            es.append(idx)
    for term,syns in SYNONYMS.iteritems():
        for word in syns:
            if ' '+word+' ' in names:
                es.append(essence.index(term))

    ingredient_essence[k] = es

with open('ingredient_essence', 'wb') as output:
    pickle.dump(ingredient_essence,output)

print('Ingredient-->Essence data saved to ingredient_essence_dict.')


ingredient_flavor = {}
for k,ingre_names in ingredient_dict.iteritems():
    flavors = []
    names = ''.join([ lmtzr.lemmatize(x) for x in ' '.join(ingre_names).lower().split(' ')])
    for keyword,v in essence_dict.iteritems():
        if keyword.replace(' ','') in names:
            flavors += v
    ingredient_flavor[k] = list(set(flavors))
with open('ingredient_flavor', 'wb') as output:
    pickle.dump(ingredient_flavor,output)

print('Ingredient-->Flavor data saved to ingredient_flavor_dict.')
