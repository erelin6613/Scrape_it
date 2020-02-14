from models import Business
from correct_base import *
from bs4 import BeautifulSoup
import re
import phonenumbers
import pyap


usa_aliases = ['United States of America', 'United States', 'USA', 'US']
uk_aliases = ['United Kingdom', 'Great Britain', 'UK', 'GB']
au_aliases = ['Australia', 'Commonwealth of Australia', 'AU']

with open('name_stop_words.txt', 'r') as file:
	name_stop_words = [r.strip() for r in file.readlines()]

with open('/home/val/Downloads/geo-key.txt', 'r') as key:
    geo_key = key.read()

with open('regex.txt', 'r') as file:
	phone_regex = [r.strip() for r in file.readlines()]

with open('email_keywords.txt', 'r') as file:
	email_keywords = [w.strip() for w in file.readlines()]

#print(regex)

class Scrape_it:

	def __init__(self, url, method='requests', country='us',
				company_name=None, category=None, geo_key=None):

		self.url = url
		self.method = method
		self.model = {'url': self.url, 'country': country, 
						'category': category, 'company_name': company_name}
		self.soup = None
		self.geo_key = geo_key


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
		self.model['housenumber'] = None
		self.model['postalcode'] = None
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

		def get_from_href(soup):
			phones = set()
			for script in soup(["script", "style"]):
				script.extract()

			try:

				for line in soup.find_all('a'):
					if line.get('href').startswith('tel:'):
						phones.add(line.get('href')[3:])

				return phones

			except AttributeError:
				return None




		def match_phones(soup):

			phones = set()
			for script in soup(["script", "style"]):
				script.extract()
			for line in soup.get_text().split('\n'):
				for match in phonenumbers.PhoneNumberMatcher(line, self.model["country"].upper()):
					phones.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))


			return phones


		self.model['phones'] = match_phones(self.soup)
		#print(self.model['phones'])
		if len(self.model['phones']) == 0:
			self.model['phones'] = get_from_href(self.soup)

	
	def find_address(self):

		def find_base(soup, country='us'):

			for script in soup(["script", "style"]):
				script.extract()
			#print(soup)
			text = soup.get_text()
			address = ''

			#for line in text:
			adr = pyap.parse(text, country='us')
			if len(adr) > 0:
				for item in adr:
					address = address+' '+str(item)

			return address

		def define_country(address):

			for alias in usa_aliases:
				if alias in self.model['address']:
					return 'us'

			for alias in uk_aliases:
				if alias in self.model['address']:
					return 'gb'

			for alias in au_aliases:
				if alias in self.model['address']:
					return'au'

			return None

		self.model['address'] = find_base(self.soup, self.model['country'])

		if self.model['country'] == None:
			self.country = define_country(self.model['address'])




	def find_email(self):

		def get_all_emails(soup):

			emails = set()

			email_pattern = '[A-Za-z0-9]*@{1}[A-Za-z0-9]*\.(com|org|de|edu|gov|uk|au){1}'
			#email_pattern = re.compile(email_pattern)
			#email_pattern = r'[A-Za-z0-9]*@{1}[A-Za-z0-9]*\.(com|org|de|edu|gov|uk|au|){1}\.?(uk|au)?'
			for script in soup(["script", "style"]):
				script.extract()

			for each in soup.get_text().split('\n'):
				email_re = re.search(email_pattern, each)
				if email_re:
					if len(email_re.group(0)) > 5 and len(email_re.group(0)) < 75:
						emails.add(email_re.group(0))

			return emails

		def keep_with_keywords(emails, keywords):

			for word in keywords:
				if word in ''.join(list(emails)):
					for email in emails:
						if word in email:
							return email

			return list(emails)[0]

		self.model['email'] = keep_with_keywords(get_all_emails(self.soup), keywords=email_keywords)




	def scrape(self):

		self.soup = self.get_soup()
		self.init_model()
		self.logging()
		self.find_address()
		self.find_phones()
		self.find_email()
		for key, val in self.model.items():
			print(key, ':', val)


