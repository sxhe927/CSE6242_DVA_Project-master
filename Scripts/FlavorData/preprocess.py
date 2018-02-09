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

###Load book data
print('Loading book data ...')
book = ''
with open('flavor_book.txt','rb') as input:
    book = input.read().replace('\n',' ')

l = book.split('Natural occurrence')
fl = filter(lambda x: "Not reported found in nature" not in x and "EXTRACT" not in x and 'not found in nature' not in x, l)
sfl = filter(lambda x: 'Synonyms' in x, fl)

###Build flavor dictionary
with open('replace.csv','rb') as file:
    replacements = [x.strip().split(',') for x in file.readlines()]

flavor_dict = {}
useless = [": Data not found.", ": n/a", ": Reported found in nature.", ": Not reported found naturally.", ": Natural", ": No data found.", ": Not reported found nature."]

for i in range(1,len(sfl)-1):
    line_split = sfl[i].split('Synonyms')[0].strip().split('  ')
    cas_no = ''
    cas_no_match = re.findall(r'CAS No.: CoE No.: (?: |a\t  )(.+)? (?:[0-9]+|n/a)(?: |  | n/a  )FL No.:',sfl[i])
    if not cas_no_match: cas_no_match = re.findall(r'CAS No.: (.+)? FL No.:',sfl[i])
    if cas_no_match: cas_no = cas_no_match[0].replace('\xe2\x80\x91', '-')
    v = sfl[i+1].split('Synonyms')[0].strip().split('  ')[0]
    if  v not in useless:
        v =  v[1:].strip().replace('Reported found in ', '').replace('Reportedly present in ','').replace('Reported present in ', '').replace(', and',',').replace(' and ', ', ').replace(';',',').replace('.','').lower().strip()
        v = re.sub(r'\([^a-zA-Z]+%\)|also .+ in|reported .+ in','',v)
        v = re.sub(r'[\(\)0-9]','',v)
        #Make List
        v = map(lambda x: reduce(lambda a,b: lmtzr.lemmatize(a.strip())+' '+lmtzr.lemmatize(b.strip()), filter(lambda w: w not in stopwords.words('English'),x.split(' '))).strip(), v.split(','))
        keywords = [x.encode('utf-8') for x in  v]
        for pair in replacements:
            keywords = [x.replace(pair[0],pair[1]) for x in keywords]
        if len(line_split) == 2:
            flavor_dict[line_split[1]] = {'Natural_occ':keywords,'CAS_No':cas_no}
        else:
            flavor_dict[line_split[len(line_split)-1]] = {'Natural_occ':v,'CAS_No':cas_no}

###Save raw flavor_dict
with open('flavor_dict', 'wb') as output:
    pickle.dump(flavor_dict,output)

print('Raw flavor data saved to flavor_dict.')

###Write Essence_raw
essence_raw = []
excluded = ['oil','oils','juice', 'canned']

for v in flavor_dict.values():
    essence_raw += v['Natural_occ']

essence_raw = list(set(essence_raw))

for i,v in enumerate(essence_raw):
    essence_raw[i] = ' '.join([lmtzr.lemmatize(x) for x in v.split(' ')])

for item in essence_raw:
    words = item.split(' ')
    if words[-1] in excluded:
        essence_raw[essence_raw.index(item)] = ' '.join(words[:-1])

essence_raw = list(set(essence_raw))
essence_raw.sort()
with open('essence_raw.csv', 'w') as output:
    for value in essence_raw:
        output.write(value+'\n')
print('Raw essence data saved to file essence_raw.csv')

###Botanical List
botanic_l = book.split('Botanical name:')
botanic_dict = {}

for i in range(0, len(botanic_l)-1):
    name = botanic_l[i].split('  ')[-1:][0].strip()
    if i == 0: name = 'ACACIA GUM'
    botanic_dict[name] = {'botanic_name':'','description':'','composition':''}
    line = botanic_l[i+1]
    botanic_name = re.findall(r'^(.+?)(?:Botanical family:|CAS No\.:)', line)
    description = re.findall(r'Description:(.+?)(?:Derivatives:|Derivative names:|Consumption:)', line)
    composition = re.findall(r'(?:Composition:|Essential oil composition:)(.+?)(?:Aroma threshold values:|  )', line)
    if botanic_name: botanic_dict[name]['botanic_name'] = botanic_name[0].strip()
    if description: botanic_dict[name]['description'] = description[0].strip()
    if composition: botanic_dict[name]['composition'] = composition[0].strip()
    botanic_dict[name]['i'] = i+1

with open('botanic_raw.csv', 'w') as output:
    for key in botanic_dict:
        output.write(str(botanic_dict[key]['i']) + ',\"' + key + '\",\"' + botanic_dict[key]['botanic_name'] + '\",\"' + botanic_dict[key]['description'] + '\",\"' + botanic_dict[key]['composition'] + '\"\n')
print('Raw botanic entries saved to file botanic_raw.csv')



# set(reduce(lambda a, b: set(a).union(set(b)), (x['dishTypes'] for x in filter(lambda x: 'dishTypes' in x, recipes))))

# Depracated method
# ### Output Raw essence data
# with open('ingredient_essence_raw.csv', 'w') as output:
#     for k in ingredient_essence:
#         output.write('\"' + str(k) + '\",\"' + ', '.join(ingredient_dict[k]).encode('utf-8') + '\",\"' + ingredient_essence[k].encode('utf-8') + '\"\n')

# ### Load Essence Data
# with open('ingredient_essence_temp.csv', 'r') as file:
#     content = file.readlines()

# ingredient_essence = {}

# essence = [x.strip() for x in content]
# for line in content:
#     ingredient_essence[int(line.split(',')[0])]=[reduce(lambda a,b : lmtzr.lemmatize(a)+' '+lmtzr.lemmatize(b),x.strip().split(' ')) for x in line.split(',')[1:]]







