# DVA_Project
This is the repository for group project for Data&Visual Analytics. 

# Data Extraction/Scraping Data
You first need an API key from Spoonacular. 

The Spoonacular API can be accessed using unirest. Install unirest using `pip install unirest` (Ideally you want to use a virtual environment).

The script for scraping recipes can be found at [DataExtraction/scrapeRecipe.py](DataExtraction) folder.

Each recipe has a unique ID, and the script below uses IDs. 

## First time Use:
Specify how many recipes and the starting ID `$ python scrapeRecipe.py <number of recipes> <start id>`

## Consequent Uses:
`$ python scrapeRecipe.py <number of recipes> <start id>`

This time you may only specify number of recipes and leave the start ID. When start ID is not specified, the program automatically picks up from where the latest file left at, and scrape recipes after that. 

## Data Collected and Log file:
Collected data will be put in DataExtraction/Recipes/ folder. The log file keeps track of file ID, start/end index, and the list of IDs that were failed to retrieved. 

However, if you are able to get bulk data from Spoonacular, then you don't need the step above.

# Data Processing

### Use `$python DataExtraction/process.py` to process scraped data.
 
This will yeild `recipe_dump`, `ingredient_dict`


### Use `$python FlavorData/preprocess.py` to preprocess flavor data.

This will yeild `flavor_dict`, `essence_raw`
Update `replace.csv` for keyword replacements, which is usually derived from `essence_raw`. If you updated this file, re-run this preprocess step. 
Save manually curated `essence_raw to` `essence_manual`

### Use `$python FlavorData/postprocess.pu` to postprocess flavor data.

This will yeild `essence`, `essence_dict`, `ingredient_essence`

### Manually classify essence to obtain `essence_types.csv`

## Run Django APP
Go to the app folder `APP/cse6242`, then run `$python manage.py runserver`
## Model Initialization
If the database is empty, you will need to initilize it with the files produced above. Initilize the models as suggested in the initialization page. You will need to initialize them in a column manner, from left to right: 

`Essence-->Compounds-->Ingredients-->Recipes-->PMI-->Ingredient Frequency`

As some of these models requires previous models to compute. 

# Use the APP
After loading all the models, you can now enter the APP page. Here you can specify an ingredient, and hit submit. This will give you recommendations from a range of ingredient types. On the right there is also a visualization of the essences of those ingredients, where the edge width corresponds to the number of shared chemical compounds. Note that sometimes even sharing one compound can make a difference. Therefore you can lower the edge threshold to include more/fewer edges. More edges will be slower though. 

You can select additional ingredients and include them in the cart. The network will automatically highlight your selections, and show you the connections between them!

Finally you can use your basket to find matching recipes by pressing the get recipes button.

# Recipe Page
This page displays all the recipes that might interest you. Due to the database size, we had to simply include a hyperlink to the spoonacular recipe pages. Some of the recipes may already be removed from their website. 
