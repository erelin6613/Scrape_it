from models import Business
from correct_base import *
from bs4 import BeautifulSoup
import re

with open('name_stop_words.txt', 'r') as file:
	name_stop_words = [r.strip() for r in file.readlines()]

with open('/home/val/Downloads/geo-key.txt', 'r') as key:
    geo_key = key.read()

with open('regex.txt', 'r') as file:
	phone_regex = [r.strip() for r in file.readlines()]

#print(regex)

class Scrape_it:

	def __init__(self, url, method='requests', country='us',
				company_name=None, category=None):

		self.url = url
		self.method = method
		#self.country = country
		#self.company_name = company_name
		#self.category = category
		self.model = {'url': self.url, 'country': country, 
						'category': category, 'company_name': company_name}
		self.soup = None


	def init_model(self):

		self.model['url'] = self.url
		self.model['company_name'] = self.model['company_name']
		self.model['country'] = self.model['country']
		self.model['category'] = self.model['category']
		self.model['contact_link'] = None
		self.model['phones'] = None
		self.model['address'] = None
		self.model['state'] = None
		self.model['county'] = None
		self.model['city'] = None
		self.model['street'] = None
		self.model['house_number'] = None
		self.model['zip'] = None
		self.model['district'] = None
		self.model['email'] = None
		self.model['facebook'] = None
		self.model['instagram'] = None
		self.model['linkedin'] = None
		self.model['pinterest'] = None
		self.model['twitter'] = None
		self.model['youtube'] = None
		self.model['faq_link'] = None
		self.model['privacy_link'] = None
		self.model['return_link'] = None
		self.model['shipping_link'] = None
		self.model['terms_link'] = None
		self.model['warranty_link'] = None
		self.model['faq_text'] = None
		self.model['privacy_text'] = None
		self.model['return_text'] = None
		self.model['shipping_text'] = None
		self.model['terms_text'] = None
		self.model['warranty_text'] = None

	def logging(self):

		print('Scraping', self.url, '...')
		#print(self.get_soup())


	def get_soup(self):

		if self.method == 'requests':
			import requests
			r = requests.get(self.url)
			soup = BeautifulSoup(r.text, 'lxml')
		if self.method == 'webdriver':
			from selenium import webdriver
			options = webdriver.ChromeOptions()	
			options.add_argument('headless')
			driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
			driver.get(self.url)
			soup = BeautifulSoup(driver.page_source, 'lxml')
		
		return soup

	def clean_name(self):

		delims = ['-', '|', ':']

		for d in delims:
			if d in self.model['company_name']:
				for i, s in enumerate(self.model['company_name'].split(d)):
					if len(set(name_stop_words).intersection(s.split(' '))) > 0:
						print(set(name_stop_words).union(s.split(' ')))
						break
					self.model['company_name'] = self.model['company_name'].split(d)[i]
					break


		return self.model.company_name



	def get_name(self):

		metas_og = ['og:site_name', 'og:title']
		metas = ['title', 'name']
		for meta in metas_og:
			if self.model['company_name'] == None or self.model['company_name'] == '':
				self.model['company_name'] = self.soup.find('meta').get('content')
				#self.company_name = self.soup.find('meta', attrs={'property': meta}).get('content')

		for meta in metas:
			if self.model['company_name'] == None or self.model['company_name'] == '':
				self.model['company_name'] = self.soup.find('meta', attrs={'name': meta}).get('content')

		self.model['company_name'] = self.clean_name()
		self.model['company_name'] = self.model['company_name']

	def find_phones(self):

		def match_phones(soup):

			phones = set()
			for line in soup.get_text().split('\n'):
				for pattern in phone_regex:
					phone_re = re.search(pattern, line)
					if phone_re:
						if len(phone_re.group(0)) > 9 and len(phone_re.group(0)) < 15:
							phones.add(phone_re.group(0).strip().replace(' ', ''))

			return phones





		self.model['phones'] = match_phones(self.soup)





	def scrape(self):

		self.soup = self.get_soup()
		self.init_model()
		self.logging()
		self.find_phones()
		print(self.model)


