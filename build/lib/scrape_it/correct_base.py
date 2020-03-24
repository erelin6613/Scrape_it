import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm, tqdm_pandas
import json
import numpy as np

#with open('geo-key.txt', 'r') as key:
#	geo_key = key.read()

email_keywords = ['info', 'help', 'support']

usa_aliases = ['United States of America', 'United States', 'USA', 'US']
uk_aliases = ['United Kingdom', 'Great Britain', 'UK', 'GB']
au_aliases = ['Australia', 'Commonwealth of Australia', 'AU']


def return_phone(string):
	if string.replace('\n', '').isdigit():
		return string.strip()
	elif len([s for s in string.split() if s.isdigit()]) > 9 and len([s for s in string.split() if s.isdigit()]) < 14:
		digits = [s for s in string.split() if s.isdigit()]
		digits = ''.join(digits)
		try:
			return digits
		except Exception as e:
			print(e)
			return digits
	else:
		return None


def clean_texts(frame):

	cols = ['faq', 'privacy_policy', 'return_policy', 'shipping', 
			'terms and conditions', 'warranty']

	for ind in frame.index:
		for col in cols:
			if str(frame.loc[ind, col]) != 'nan':
				if 'JavaScript' in str(frame.loc[ind, col]):
					frame.loc[ind, cols] = None
					break
				if 'nan ' in str(frame.loc[ind, col]):
					frame.loc[ind, col] = str(frame.loc[ind, col]).replace('nan ', 'Company')
				if "nan's" in str(frame.loc[ind, col]):
					frame.loc[ind, col] = str(frame.loc[ind, col]).replace("nan's", "Company's")

	return frame

def extend_addresses(frame):


	for ind in tqdm(frame.index):
		if str(frame.loc[ind, 'address']) != 'nan':
			address = check_address(frame.loc[ind, 'address'])
			try:
				if len(address.keys()) > 0:
					for key in address.keys():
						frame.loc[ind, key] = address[key]
			except Exception:
				pass

	return frame

def process_phones(phone, country=None):

	if country:
		country=str(country)

	phone = phone.replace('-', ' ').replace('(', ' ').replace(')', ' ')
	phone = phone.replace('.', ' ').replace(',', ' ').replace('    ', ' ')
	phone = phone.strip().replace('\t', ' ').replace('  ', ' ')
	phone = phone.replace('  ', ' ').replace(':', '')
	if phone.startswith('+'):
		return phone
	if country.lower() == 'uk' or country.lower() == 'gb':
		if phone.startswith('0'):
			phone = '+44 '+phone[1:]
		else:
			phone = '+44 '+phone
	if country.lower() == 'us' or country.lower() == 'ca' or country.lower() == 'usa':
		if phone.startswith('0') or phone.startswith('1'):
			phone = '+1 '+phone[1:]
		else:
			phone = '+1 '+phone
	if country.lower() == 'au':
		if phone.startswith('0'):
			phone = '+61 '+phone[1:]
		else:
			phone = '+61 '+phone

	if len(phone.strip(' ')) > 14 and len(phone.strip(' ')) < 11:
		return None

	return phone

def count_digits(string):

	string = str(string)
	if string.replace('\n', '').isdigit():
		return len(string.strip())
	return len([s for s in string if s.isdigit()])


def check_address(adr, geo_key=None):

	if geo_key:

		r = requests.get(f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={geo_key}&searchtext={adr}')
		print(r.url)
		#address = {}

		try:
			return json.loads(r.text)['Response']['View'][0]['Result'][0]['Location']['Address']
		except Exception:
			return adr
	else:
		return adr


def define_country(address):

	for alias in usa_aliases:
		if alias in address:
			return 'us'

	for alias in uk_aliases:
		if alias in address:
			return 'gb'

	for alias in au_aliases:
		if alias in address:
			return 'au'

	return None