
import unirest, io, json, time, os, sys

#find file subscripts
files = [x for x in os.listdir('./Recipes') if x.endswith(".txt")];
sub = len(files) + 1
if sub == 1 : # provide starting index as the second argument
    if (len(sys.argv) != 3):
         sys.exit("Please specify the starting index as the second argument to initialize.")
    startID = int(sys.argv[2])
else :
    files.sort()
    lastFile = files[len(files)-1]
    if (len(sys.argv) == 3):
        startID = int(sys.argv[2])
    else:
        startID = int(lastFile.split('_')[3][:-4])+1

endID = startID + int(sys.argv[1])-1


failures = []
counter  = 0
total = 0

#write data
fileName = 'Recipes/rdata_'+ '{:03d}'.format(sub) +'_'+ str(startID) + '_' + str(endID) +'.txt'
with open(fileName, 'w') as output:
    sys.stdout.write('[')
    sys.stdout.flush()
    for i in range(startID,endID+1):
        getURL = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/"+str(i)+"/information?includeNutrition=false"
        response = unirest.get(getURL,
          headers={
            "X-Mashape-Key": "UeuShFf8SQmshs5tz2Ps5sTHWTtDp16lqHkjsnYtVX8dP3N1xR",
            "Accept": "application/json"
          }
        )
        if response.code != 404: #if successful
            json.dump(response.body, output)
            output.write('\n')
            counter = counter + 1
        else:
            failures.append(i)
        total = total + 1
        time.sleep(0.1)
        if total % 100 == 0:
            sys.stdout.write('-')
            sys.stdout.flush()
        if total % 501 == 0:
            sys.stdout.write('|')
            sys.stdout.flush()
sys.stdout.write(']\n')
#log statistics
with open('Recipes/log', 'a') as output:
    output.write('rdata_'+ '{:03d}'.format(sub) + '\t' + str(startID) + '\t' + str(endID) + '\t'+ str(counter) + '\t' + 'Failed:' + str(failures) + '\n')

print('Successfully scraped ' + str(counter) + ' recipes to file ' + fileName)

