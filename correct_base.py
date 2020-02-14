import pandas as pd
import feedparser
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm, tqdm_pandas
import json
import numpy as np

#with open('geo-key.txt', 'r') as key:
#	geo_key = key.read()

email_keywords = ['info', 'help', 'support']


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


def cleaning_step_1():
	for ind in results_data.index:

		#print(results_data.loc[ind, 'url'].split('/'))
		results_data.loc[ind, 'url'] = str(results_data.loc[ind, 'url'].split('/')[0]+'//'+results_data.loc[ind, 'url'].split('/')[2]).replace('www.', '')
		try:
			task_data.loc[ind, 'url'] = str(task_data.loc[ind, 'url'].split('/')[0]+'//'+task_data.loc[ind, 'url'].split('/')[2]).replace('www.', '')
		except Exception:
			pass
		if str(results_data.loc[ind, 'email']) != 'nan':
			email_bool = False
			for each in str(results_data.loc[ind, 'email']).split('\n'):
				if 'test' in each or 'example' in each:
					continue
				if not email_bool:
					for w in email_keywords:
						if w in each:
							email = each.strip()
							email_bool = True
							break
			try:
				assert len(email) > 0
			except Exception:
				email = str(results_data.loc[ind, 'email']).split('\n')[0].strip()

		if str(results_data.loc[ind, 'phones']) != 'nan':
			i = 1
			for phone in str(results_data.loc[ind, 'phones']).split('\n'):
				results_data.loc[ind, f'phone_{i}'] = phone
				i += 1
				if i == 7:
					break
			try:
				assert str(results_data.loc[ind, 'phone_1']) == 'nan'
				results_data.loc[ind, 'phone_1'] = str(results_data.loc[ind, 'phones']).split('\n')[0]
			except Exception:
				pass

	df = results_data.groupby('url').first()
	df.to_csv('task_companies_second_bulk.csv')

def check_address(adr):

	r = requests.get(f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={geo_key}&searchtext={adr}')
	address = {}

	try:
		return json.loads(r.text)['Response']['View'][0]['Result'][0]['Location']['Address']
	except Exception:
		return ''
	



def clean_texts():

	cols = ['faq', 'privacy_policy', 'return_policy', 'shipping', 
			'terms and conditions', 'warranty']

	for ind in results_data.index:
		for col in cols:
			if str(results_data.loc[ind, col]) != 'nan':
				if 'JavaScript' in str(results_data.loc[ind, col]):
					results_data.loc[ind, cols] = None
					break
				if 'nan ' in str(results_data.loc[ind, col]):
					results_data.loc[ind, col] = str(results_data.loc[ind, col]).replace('nan ', 'Company')
				if "nan's" in str(results_data.loc[ind, col]):
					results_data.loc[ind, col] = str(results_data.loc[ind, col]).replace("nan's", "Company's")

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
	phone = phone.strip().replace('\t', ' ').replace('  ', ' ').replace('  ', ' ')
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


def main():

	results_1, results_2 = pd.read_csv('task_companies_results.csv'), \
							pd.read_csv('task_companies_second_bulk.csv')

	phone_cols = ['phone_1', 'phone_2', 'phone_3', 
					'phone_4', 'phone_5','phone_6']

	results_1['phones'], results_2['phones'] = pd.Series(), pd.Series()

	i=0

	for frame in [results_1, results_2]:
		for ind in frame.index:
			for col in phone_cols:
				if str(frame.loc[ind, col]).lower() != 'nan':
					frame.loc[ind, col] = process_phones(frame.loc[ind, col], country=frame.loc[ind, 'country'])
					#print(results_1.loc[ind, col])
					#print(count_digits(results_1.loc[ind, col]))
					if count_digits(frame.loc[ind, col]) < 11:
						frame.loc[ind, col] = None
					print(frame.loc[ind, col])
					if str(frame.loc[ind, 'phones']).lower() != 'nan':
						frame.loc[ind, 'phones'] = str(frame.loc[ind, 'phones'])+'; '+str(frame.loc[ind, col])
					else:
						frame.loc[ind, 'phones'] = str(frame.loc[ind, col])

					if 'none' in str(frame.loc[ind, 'phones']).lower():
						frame.loc[ind, 'phones'] = ''
		frame = frame.fillna('')
		frame = frame.drop(phone_cols, axis=1)
		frame.to_csv(f'frame_{i}.csv')
		i += 1


def check_address(adr, geo_key=None):

	if geo_key:

		r = requests.get(f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={geo_key}&searchtext={adr}')
		print(r.url)
		address = {}

		try:
			return json.loads(r.text)['Response']['View'][0]['Result'][0]['Location']['Address']
		except Exception:
			return adr
	else:
		return adr


def extend_addresses(address, geo_key=None):

	adr_dict = {}

	address = check_address(address, geo_key=geo_key)
	try:
		if len(address.keys()) > 0:
			for key in address.keys():
				if key == 'Label':
					adr_dict['address'] = address[key].split(',')[0]
					continue
				if key == 'AdditionalData':
					continue

				adr_dict[key.lower()] = address[key]
	except Exception:
		adr_dict['address'] = adr_dict['address'].split(',')[0]

	return adr_dict



def main_2():
	i=0

	results_1, results_2 = pd.read_csv('frame_0.csv'), \
							pd.read_csv('frame_1.csv')

	for frame in [results_1, results_2]:
		for ind in frame.index:
			for col in frame.columns:
				if 'address' in col.lower():
					if str(frame.loc[ind, col]).lower() != 'nan':
						frame.loc[ind, col] = str(frame.loc[ind, col]).split(',')[0]

		frame.to_csv(f'check_{i}.csv')
		i+=1



if __name__ == '__main__':
	main_2()