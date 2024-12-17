## amazon review scraping & tagging

### scraping:
script that takes a list of ASINs (amazon standard identification numbers) and generates a JSON file with info & reviews for each item. uses beautifulsoup & python requests lib 

* max 100 reviews for each star rating can be scraped
* reviews are scraped in order of most recent date first
* in order to authenticate past 2nd reviews page, need to sign in to amazon, grab cookies from browser, and set in .env file. see example


#### to run
* create venv
* pip install -r requirements.txt
* python scripts/final.py



### tagging:
takes amazon review json data and generates sentiment tags (relevant terms/phrases that indicate customer sentiment towards the product), then tags the reviews 

* calls OpenAI api to generate list of 12 relevant sentiment tags according to the json data. stores the tags in a csv file.
* for each tag and each review in the json data, calls the OpenAI api to determine whether the tag applies to the review (true/false). generates a CSV file with the review id and tag.

result will be a csv table with the 12 generated tags, a csv table with data about each review, and a csv table with review id and associated tag. The last two csv tables can be joined on the id column and used for analysis or visualization.

#### to run
* run tagging scripts in order (1-3)
