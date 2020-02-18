"""
Scrape_it

Author: Valentyna Fihurska

Lisence: Apache-2.0

Scrape_it is a tool for extracting valueble information 
from the website of interest. Save your time on reading 
and crawling through the website and leave it for Scrape_it!

Find an example how to run program in the run.py
or refer to README 


Note on additional .txt files

name_stop_words.txt - Contains words to filter unneeded words
						during the search of entity's name

email_keywords.txt - Specific file to filter emails based on 
						keywords it might contain (this is
						as needed for current task)

regex.txt - some regular expressions to search phone numbers;
			at the current time is not in use, phonenumbers
			package is used instead; one of improvements
			should be a workflow which would allow efficient
			and accurate phone matching with good filter
			pipeline from 'scraping trash'
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from models import Business
from correct_base import *
from bs4 import BeautifulSoup
import re
import phonenumbers
import pyap
from address_parser import Parser
import requests
from selenium import webdriver
import json
from scrape_policy_text import _get_text_list, text_generator

parser = Parser()


with open('name_stop_words.txt', 'r') as file:
	name_stop_words = [r.strip() for r in file.readlines()]

with open('/home/val/Downloads/geo-key.txt', 'r') as key:
    geo_key = key.read()

with open('regex.txt', 'r') as file:
	phone_regex = [r.strip() for r in file.readlines()]

with open('email_keywords.txt', 'r') as file:
	email_keywords = [w.strip() for w in file.readlines()]

internal_links = {'contact_link': r'contact.*', 
					'privacy_link': r'privacy.*policy', 
					'shipping_link': r'(deliver|shiping).*(policy)*', 
					'terms_link': r'term.*(condition|use|service)', 
					'faq_link': r'(faq)|(frequently.*asked.*question)', 
					'return_link': r'return.*', 
					'warranty_link': r'(warrant)|(guarant)'}

external_links = {'twitter': 'twitter.com', 
					'facebook': 'facebook.com',
					'instagram': 'instagram.com',
					'pinterest':'pinterest.com', 
					'youtube': 'youtube.com',
					'linkedin': 'linkedin.com'}

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


	def get_soup(self, url):

		if self.method == 'requests':
			import requests
			r = requests.get(url)
			soup = BeautifulSoup(r.text, 'lxml')
		if self.method == 'webdriver':
			from selenium import webdriver
			options = webdriver.ChromeOptions()	
			options.add_argument('headless')
			driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
			driver.get(url)
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


		return self.model['company_name']


	def get_name(self):

		metas_og = ['og:site_name', 'og:title']
		metas = ['title', 'name']
		for meta in metas_og:
			if self.model['company_name'] == None or self.model['company_name'] == '':
				try:
					self.model['company_name'] = self.soup.find('meta', attrs={'property': meta}).get('content')
				except AttributeError:
					pass

		for meta in metas:
			if self.model['company_name'] == None or self.model['company_name'] == '':
				try:
					self.model['company_name'] = self.soup.find('meta', attrs={'name': meta}).get('content')
				except AttributeError:
					if self.soup.find('title'):
						if len(self.soup.find('title')) > 0:
							self.model['company_name'] = self.soup.find('title').text
		if self.model['company_name'] != None:
			self.model['company_name'] = self.clean_name()



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


		if self.model['phones']:
			self.model['phones'] = self.model['phones'].union(match_phones(self.soup))
		else:
			self.model['phones'] = match_phones(self.soup)

		if len(self.model['phones']) == 0:
			self.model['phones'] = get_from_href(self.soup)


	def find_address(self):

		def find_base(soup, country='us'):

			for script in soup(["script", "style"]):
				script.extract()
			text = soup.get_text()
			address = ''

			adr = pyap.parse(text, country='us')
			if len(adr) > 0:
				for item in adr:
					address = address+' '+str(item)

			return address



		self.model['address'] = find_base(self.soup, self.model['country'])

		if len(self.model['address']) > 0:
			if define_country(self.model['country']) != None:
				self.model['country'] = define_country(self.model['country'])


	def find_email(self):

		def get_all_emails(soup):

			emails = set()

			email_pattern = r'[A-Za-z0-9]*@{1}[A-Za-z0-9]*\.(com|org|de|edu|gov|uk|au){1}'
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

			if len(list(emails)) > 0:
				return list(emails)[0]
			return None

		self.model['email'] = keep_with_keywords(get_all_emails(self.soup), keywords=email_keywords)

	
	def find_links(self):

		def find_raw_links(soup):

			links = {}
			for each in soup.find_all('a'):
				for ext_key, ext_val in external_links.items():
					if ext_val in str(each.get('href')):
						links[ext_key] = str(each.get('href'))

				for int_key, int_val in internal_links.items():
					try:
						url = re.findall(int_val, each.get('href'))
						if len(url) > 0:
							links[int_key] = str(each.get('href'))
					except Exception:
						pass

			return links



		def build_links(links):

			for key, link in links.items():
				if key in external_links.keys():
					continue
				if link.startswith('/'):
					if self.url.endswith('/'):
						links[key] = self.url+link[1:]
					else:
						links[key] = self.url+link


				else:
					if link.startswith('http') == False and link.startswith('www') == False:
						if self.url.endswith('/'):
							links[key] = self.url+link
						else:
							links[key] = self.url+'/'+link

				links = clean_links(links)

			return links

		def clean_links(links):

			stop_attrs = ['#', '?', 'login', 'signup', 'sign-up', 'sign_up']

			for key, link in links.items():
				for attr in stop_attrs:
					if attr in link:
						links[key] = link.split(attr)[0]

			return links




		links = build_links(find_raw_links(self.soup))
		
		for key, link in links.items():
			self.model[key] = link


	def validate_address(self):

		def check_address(adr, geo_key=None):

			if geo_key:

				r = requests.get(f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={geo_key}&searchtext={adr}')

				try:
					return json.loads(r.text)['Response']['View'][0]['Result'][0]['Location']['Address']

				except Exception:
					return adr
			else:
				return adr

		def extend_addresses(address, geo_key=None):

			adr_dict = {}

			address = check_address(address, geo_key)
			try:
				if len(address.keys()) > 0:
					for key in address.keys():
						if key == 'Label':
							adr_dict['address'] = address[key].split(',')[0]
							continue
						if key == 'AdditionalData':
							continue
						if key == 'Country' and address[key] != None:
							adr_dict['country'] = define_country(address['Country'])
							continue


						adr_dict[key] = address[key]
			except Exception:
				pass


			return adr_dict



		if self.model['address'] != None and len(self.model['address']) > 0:
			for key, val in extend_addresses(self.model['address'], self.geo_key).items():
				if key.lower() == 'country' and self.model['country']:
					continue
				self.model[key.lower()] = val



	def scrape(self):

		self.soup = self.get_soup(self.url)
		self.init_model()
		self.logging()
		if self.model['company_name'] == None:
			self.get_name()
		self.find_address()
		self.find_phones()
		self.find_email()
		self.find_links()

		if self.model['address'] != None or len(self.model['address']) != 0:
			self.validate_address()

		if self.model['contact_link']:
			self.soup = self.get_soup(self.model['contact_link'])
			if self.model['address'] == None or len(self.model['address']) == 0:
				self.find_address()
				self.validate_address()
			self.find_phones()
			if self.model['email'] == None or len(self.model['email']) == 0:
				self.find_email()
		if self.method == 'requests':
			for key, val in internal_links.items():
				if self.model[key] != None:
					if 'contact' in key:
						continue
					text_key = key.split('_')[0]+'_text'
					self.model[text_key] = _get_text_list(self.model[key], method='requests')
					if self.model[text_key] != None:
						self.model[text_key] = '; '.join(text_generator(text_mas=self.model[text_key][0], 
														company_name=self.model['company_name'],
														company_website=self.model['url']))


		

		for key, val in self.model.items():
			print(key, ':', val)

		return self.model


