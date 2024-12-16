### amazon review scraping

script that takes a list of ASINs (amazon standard identification numbers) and generates a JSON file with info & reviews for each item. uses beautifulsoup & python requests lib 

* max 100 reviews for each star rating can be scraped
* reviews are scraped in order of most recent date first
* in order to authenticate past 2nd reviews page, need to sign in to amazon, grab cookies from browser, and set in .env file. see example


#### to run
* create venv
* pip install -r requirements.txt
* python scripts/final.py
