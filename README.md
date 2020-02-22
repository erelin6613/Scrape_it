# Scrape_it

Scrape_it is a tool for extracting valueble information from the website of interest. Save your time on reading and crawling through the website and leave it for Scrape_it!

# Installation
Scrape_it is avalable on Pypi, you can install it using pip:
```sh
pip install scrape-it
```
Install the lastest version:
```sh
pip install git+https://github.com/erelin6613/Scrape_it
```


# Scrape_it object

As a baseline Scrape_it relies on the model (dictionary) which could be customized although specific methods should be defined too.

Currently the object's base-line model is set up to scrape contact information, address, social media links, links for website's policies pages and if posiible condence its' texts.

To initialize the object specify the url as a string. For more precision provide some more details if known:

- country: 'us' for United States of America, 'gb' for Great Britain/United Kingdom, 'au' for Australia
- geo_key: API key for address verification, test is set up to work with [this](https://developer.here.com) API
- method: 'requests' for usual get request or 'webdriver' for request capable of rendering JavaScript code and dynamically changing webpages

# Usage

Initialize Scrape_it object (find an example in run.py)

```sh
from scrape_it import Scrape_it

with open('/home/val/Downloads/geo-key.txt', 'r') as key:
    geo_key = key.read()

scrape_it = Scrape_it(url='https://www.all-wall.com', country='us', geo_key=geo_key, method='webdriver')

scrape_it.scrape()
```

The output will like this:

```sh
Scraping https://www.all-wall.com ...
url : https://www.all-wall.com
country : us
category : None
company_name : All
contact_link : None
phones : {'+18009290927'}
address : 6561 W Post Rd
state : NV
county : Clark
city : Las Vegas
street : W Post Rd
housenumber : 6561
postalcode : 89118
district : Spring Valley
email : None
facebook : https://www.facebook.com/AllWallEquipment
instagram : https://www.instagram.com/allwall_inc/
linkedin : None
pinterest : None
twitter : https://twitter.com/AllWall_Inc
youtube : https://www.youtube.com/channel/UCsNTFJvx3Wi8D3I92pYVZSg
faq_link : None
privacy_link : https://www.iubenda.com/privacy-policy/569672
return_link : None
shipping_link : None
terms_link : None
warranty_link : None
faq_text : None
privacy_text : None
return_text : None
shipping_text : None
terms_text : None
warranty_text : None

```

# Contributing
The Scrape_it is by no means a perfect package and can be improved for sure. If you have any ideas, issues or would like to improve code or documentation please feel free to open issue or pull request. It is my honor to be at help if I can.

# FAQ

#### Q: The object returns the emplty dictionary. What do I do?
###### A: It could be the case the tools used did not find anything though it is certainly an exception rather than a rule. What you can try though: use 'webdriver' method to ensure JavaScript is rendered too, try specify the country, use proxy/VPN in case the website might block requests from your location

#### Q: Should I pass a root link or any would work?
###### A: Yes, for now at least. Scrape_it will scrape some information still but it relies on finding additional links to scrape the most information possible and I did not set the pipeline to process non-root links yet (I am working on it)
