from scrape_it import Scrape_it

with open('/home/val/Downloads/geo-key.txt', 'r') as key:
    geo_key = key.read()

scrape_it = Scrape_it(url='https://www.all-wall.com', country='us', geo_key=geo_key, method='webdriver')

scrape_it.scrape()