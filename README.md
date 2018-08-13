# Myanmar-FB-Page-Scraper

facebook_scraper.ipynb is used to scrape posts, comments and reactions from public Facebook pages. It calls scraper.py to scrape the FB pages. scraper.py calls converter.py and uni_ecoder.py to convert from Zawgyi to Unicode.

You have to fill in these two lines in scraper.py and facebook_scraper.ipynb using the app id and app secret from your own FB app. Register you own app [here](https://developers.facebook.com/docs/apps/#register). 

app_id = ""
app_secret = ""

facebook_analyser.ipynb is used to make simple plots from the CSv files produced after scraping the pages. The data folder contains scraped page data.
