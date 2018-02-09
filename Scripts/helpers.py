import pickle
import numpy as np
import networkx as nx

with open('FlavorData/flavor_dict', 'r') as infile:
    flavor_dict = pickle.load(infile)

with open('FlavorData/essence_dict', 'r') as infile:
    essence_dict = pickle.load(infile)

with open('FlavorData/ingredient_flavor', 'r') as infile:
    ingredient_flavor = pickle.load(infile)

with open('DataExtraction/ingredient_dict', 'r') as infile:
    ingredient_dict = pickle.load(infile)

with open('DataExtraction/ingredient_distr', 'r') as infile:
    ingredient_distr_dict = pickle.load(infile)

###Build Match Matrix F X I
F = len(flavor_dict)
I = len(ingredient_flavor)
ingredient_idx = ingredient_flavor.keys()
flavor_m = np.zeros((F,I))

for i,idx in enumerate(ingredient_idx):
    for f in ingredient_flavor[idx]:
        flavor_m[f,i] = 1

###Recommendation
coG = nx.read_edgelist('DataExtraction/network/ingredient_net.csv', delimiter=',', nodetype=int, data=(('weight',float),))

cc_co_m = np.dot(flavor_m.T,flavor_m)

test_id = 11529
PMI_neighbors = [(x[0], x[1]['weight']) for x in coG[test_id].items()]
PMI_neighbors.sort(key = lambda x: x[1], reverse = True)
PMI_neighbors = filter(lambda x: ingredient_distr_dict[x[0]] > 50, PMI_neighbors)
for t in PMI_neighbors[:50]:
    print(ingredient_dict[t[0]],t[1],ingredient_distr_dict[t[0]])

result = [ingredient_dict[x[0]] for x in filter(lambda x: cc_co_m[ingredient_idx.index(x[0]),ingredient_idx.index(test_id)] >1 ,PMI_neighbors)[:4]]


###CCCOM to graph
label_idx = set()
with open('flavor_net_raw.csv','w') as output:
    output.write('Target,Source,Weight\n')
    for x in range(I):
        for y in range(I):
            if x < y and cc_co_m[x,y] != 0 and ingredient_distr_dict[ingredient_idx[y]] > 100 and ingredient_distr_dict[ingredient_idx[x]] > 100:
                label_idx.add(ingredient_idx[x])
                label_idx.add(ingredient_idx[y])
                output.write(str(ingredient_idx[x])+','+str(ingredient_idx[y]) +',' + str(cc_co_m[x,y]) + '\n')

with open('flavor_net_raw_labels.csv','w') as output:
    output.write('Id,Name,Occurrence\n')
    for idx in label_idx:
        output.write(str(idx) + ',' + ingredient_dict[idx][0] + ',' + str(ingredient_distr_dict[idx]) + '\n')



### Essence 

F = len(flavor_dict)
I = len(essence_dict)
ingredient_idx = essence_dict.keys()
flavor_m = np.zeros((F,I))

for i,idx in enumerate(ingredient_idx):
    for f in essence_dict[idx]:
        flavor_m[f,i] = 1

dist = zip([np.dot(i.T,flavor_m[:,test_id]) for i in flavor_m.T],range(len(ingredient_idx)))
dist.sort(key=lambda x: x[0], reverse=True) #first 5 match
for i in [(ingredient_idx[x[1]],x[0]) for x in dist[:50]]:
    print(i)


### Test
test_id = ingredient_idx.index(1123) #9152 lemon, 11215 garlic, 9037 avocado, 1123 egg, 11090 broccoli

### Euclidean Distance
dist = zip([LA.norm(i-flavor_m[:,test_id])for i in flavor_m.T],range(len(ingredient_idx)))
dist.sort(key=lambda x: x[0]) #first 5 match
for i in [ingredient_dict[ingredient_idx[x[1]]] for x in dist[:20]]:
    print(i)

### Shared Counts
dist = zip([np.dot(i.T,flavor_m[:,test_id]) for i in flavor_m.T],range(len(ingredient_idx)))
dist.sort(key=lambda x: x[0], reverse=True) #first 5 match
for i in [(ingredient_dict[ingredient_idx[x[1]]],x[0]) for x in dist[:30]]:
    print(i)

### Normalize by Distribution
#max_occur = max(ingredient_distr.values())
dist = zip([np.dot(v.T,flavor_m[:,test_id]*(ingredient_distr[ingredient_idx[i]]>100)) for i,v in enumerate(flavor_m.T)],range(len(ingredient_idx)))
dist.sort(key=lambda x: x[0], reverse=True) #first 5 match
for i in [(ingredient_dict[ingredient_idx[x[1]]][0],ingredient_essence[ingredient_idx[x[1]]],x[0]) for x in dist[:30]]:
    print(i)

###Load Ingredient Distribution
with open('ingredient_distribution.csv', 'r') as file:
    content = file.readlines()

ingredient_distr = {}

for line in [x.strip() for x in content] :
    ingredient_distr[int(line.split(',')[0])] = float(line.split(',')[1])

