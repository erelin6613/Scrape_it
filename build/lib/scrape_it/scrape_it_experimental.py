"""
Scrape_it

Author: Valentyna Fihurska

Lisence: Apache-2.0

Scrape_it is a tool for extracting valueble information 
from the website of interest. Save your time on reading 
and crawling through the website and leave it for Scrape_it!

Find an example how to run program in the run.py
or refer to README 


Note on additional .txt files in regex directory

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

address.txt - some regular expressions to match addresses,
                not perfect expesially given the diversity
                of different address formats accross 
                different countries

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

from .correct_base import process_phones, define_country
from .regex import *
from bs4 import BeautifulSoup
import re
import phonenumbers
import pyap
import requests
import json
import os
from selenium import webdriver
from .scrape_policy_text import _get_text_list, text_generator
import tldextract

"""
with open('regex/name_stop_words.txt', 'r') as file:
    name_stop_words = [r.strip() for r in file.readlines()]

with open('regex/phones_regex.txt', 'r') as file:
    phone_regex = [r.strip() for r in file.readlines()]

with open('regex/email_keywords.txt', 'r') as file:
    email_keywords = [w.strip() for w in file.readlines()]

with open('regex/js_keywords.txt', 'r') as file:
    js_keywords = [w.strip() for w in file.readlines()]
"""


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
                    'pinterest': 'pinterest.com', 
                    'youtube': 'youtube.com',
                    'linkedin': 'linkedin.com'}


class Scrape_it:

    def __init__(self, url, method='requests', country='us',
                company_name=None, category=None, geo_key=None,
                verbose=0, driver=None):

        self.url = url
        self.method = method
        #self.model = {'url': self.url, 'country': country, 
        #                'category': category, 'company_name': company_name}
        self.soup = None
        self.geo_key = geo_key
        self.verbose = verbose
        self.driver = driver
        self.get_soup()


    def logging(self):
        """
        Log some text while scraping if verbose is set to 1
        """

        if self.verbose == 1:
            print('Scraping', self.url, '...')

    def define_domain(self):
        """
        Define domain name of the link
        """

        def get_domain(url):
            domain = tldextract.extract(str(url)).domain+'.'+tldextract.extract(str(url)).suffix
            return ['https://'+domain, 'http://'+domain, 'https://www.'+domain]

        return get_domain(self.url)

        #self.model['url'] = get_domain(self.url)

    def get_soup(self):
        """
        Gets soup object depending on the method
        """
        url = self.define_domain(self.url)
        if self.method == 'requests':
            import requests
            try:
                for link in url:
                    r = requests.get(link)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, 'lxml')
                        break

            except Exception as e:
                print(e, link)
            
        if self.method == 'webdriver':
            from selenium import webdriver
            options = webdriver.ChromeOptions() 
            options.add_argument('headless')
            self.driver = webdriver.Chrome(executable_path='./chromedriver', 
                                            options=options)

            for link in url:
                try:
                    self.driver.get(link)
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    break
                except Exception as e:
                    print(e, link)
                
        try:
            assert soup is not None
            return soup
        except Exception:
            return

    #def scrape(self):

        #self.soup = self.get_soup(self.url)





class CustomScrape(Scrape_it):

    def __init__(self):
        super.__init__()

        self.model = {'url': self.url, 'country': country, 
                        'category': category, 'company_name': company_name}


    def init_model(self):
        """
        Current task of mine is reflected in the model; it is planned
        by me to export models to seperate file and use different onces
        as need or to simplify the process of defining the model and
        needed methods to execute
        """

        self.model['url'] = self.url
        self.model['company_name'] = self.model['company_name']
        self.model['country'] = self.model['country']
        self.model['category'] = self.model['category']
        self.model['contact_link'] = None
        self.model['phones'] = None
        self.model['phone_1'] = None
        self.model['phone_2'] = None
        self.model['phone_3'] = None
        self.model['phone_4'] = None
        self.model['phone_5'] = None
        self.model['phone_6'] = None
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

    def clean_name(self):
        """
        Since company name is scraped from code too it can
        be messy and needs to be cleaned from short descriptions
        """

        delims = ['|', '-', ':']

        if self.model['company_name']:

            for d in delims:
                if d in self.model['company_name']:
                    for i, s in enumerate(self.model['company_name'].split(d)):
                        same_words = set(name_stop_words).intersection(s.split(' '))
                        if len(same_words) > 0:
                            break
                        self.model['company_name'] = self.model['company_name'].split(d)[i]
                        break
        return self.model['company_name']

    def get_name(self):
        """
        Get company name from the most likely places in html it could be found
        """
        for script in self.soup(["script", "style"]):
            script.extract()

        metas_og = ['og:site_name', 'og:title']
        metas = ['title', 'name']
        for meta in metas_og:
            if self.model['company_name'] is None \
            or self.model['company_name'] == '':
                try:
                    meta_name = self.soup.find('meta', attrs={'property': meta})
                    self.model['company_name'] = meta_name.get('content')
                except AttributeError:
                    pass

        for meta in metas:
            if self.model['company_name'] is None \
            or self.model['company_name'] == '':
                try:
                    meta_name = self.soup.find('meta', attrs={'name': meta})
                    self.model['company_name'] = meta_name.get('content')
                except AttributeError:
                    if self.soup.find('title'):
                        if len(self.soup.find('title')) > 0:
                            title = self.soup.find('title')
                            self.model['company_name'] = title.text
        if self.model['company_name'] is not None:
            if 'forbidden' in self.model['company_name'].lower() or\
            'ngMeta' in self.model['company_name']:
                self.model['company_name'] = None
            if self.model['company_name']:
                self.model['company_name'] = self.clean_name().strip()

    def find_phones(self):

        def get_from_href(soup):
            """
            If phonenumbers package could not find any phone numbers
            there could be some embedded in links as in 
            <a href="tel:+18887896541">
            """
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
            """
            Find phones using phonenumbers package, location is provided from
            model's country value
            """
            phones = set()
            for script in soup(["script", "style"]):
                script.extract()
            for line in soup.get_text().split('\n'):
                matches = phonenumbers.PhoneNumberMatcher(line, str(self.model["country"]).upper())
                for match in matches:
                    phones.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))

            return phones

        self.model['phones'] = get_from_href(self.soup)
        if self.model['phones']:
            self.model['phones'] = self.model['phones'].union(match_phones(self.soup))
        else:
            self.model['phones'] = match_phones(self.soup)

    def find_address(self):

        def find_regex(soup):
            """
            Find address with regular expression(s) specified in regex/address.txt
            """
            try:
                address_regex = r'^([0-9\-/]+) ?([A-Za-z](?= ))? (.*?) ([^ ]+?) ?((?<= )[A-Za-z])? ?((?<= )\d*)?$\
                                    ^([A-Za-z]+ ?)+[0-9]{3,6}$\
                                    ^([A-Za-z]+ ?)$'
            except Exception:
                pass
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            address = re.search(address_regex, text)
            if address:
                address = address.group(0)
            else:
                address = None

            return address

        def find_base(soup, country='us'):
            """
            Find addresses using pyap package
            """
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            address = ''

            adr = pyap.parse(text, country='us')
            if len(adr) > 0:
                for item in adr:
                    address = address+' '+str(item)

            return address

        if self.model['address'] is None:
            self.model['address'] = find_regex(self.soup)
            if self.model['address'] is None:
                base = find_base(self.soup, self.model['country'])
                self.model['address'] = base

        if len(self.model['address']) > 0:
            if define_country(self.model['country']) is not None:
                self.model['country'] = define_country(self.model['country'])

    def find_email(self):

        def get_all_emails(soup):
            """
            Get set of emails using regular expression
            """

            emails = set()

            email_pattern = r'[A-Za-z0-9]*@{1}[A-Za-z0-9]*\.(com|org|de|edu|gov|uk|au|net|me){1}'
            for script in soup(["script", "style"]):
                script.extract()

            for each in soup.get_text().split('\n'):
                email_re = re.search(email_pattern, each)
                if email_re:
                    if len(email_re.group(0)) > 5 \
                    and len(email_re.group(0)) < 75:
                        emails.add(email_re.group(0))

            return emails

        def keep_with_keywords(emails, keywords):
            """
            Filter emails and keep one of the set found, as for my task
            either one with keywors specified in regex/email_keywors.txt
            or the first one if there are none which contain needed
            keywords
            """

            for word in keywords:
                if word in ''.join(list(emails)):
                    for email in emails:
                        if word in email:
                            return email

            if len(list(emails)) > 0:
                return list(emails)[0]
            return None
        mails = get_all_emails(self.soup)
        self.model['email'] = keep_with_keywords(mails, email_keywords)
 
    def find_links(self):

        def find_raw_links(soup):
            """
            Find links:
                external: social media links
                internal: links to policies, faq, etc
            """

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
            """
            Build links from raw scraped hfer attributes
            """

            for key, link in links.items():
                if link.startswith('http') or link.startswith('www'):
                    links[key] = self.fix_link(link)
                    continue
                if link.startswith('//'):
                    links[key] = self.fix_link(link[2:])
                    continue
                if key in external_links.keys():
                    continue
                if link.startswith('/'):
                    if self.url.endswith('/'):
                        links[key] = self.url+link[1:]
                    else:
                        links[key] = self.url+link
                else:
                    if link.startswith('http') is False \
                    and link.startswith('www') is False:
                        if self.url.endswith('/'):
                            links[key] = self.url+link
                        else:
                            links[key] = self.url+'/'+link

                links = clean_links(links)

            return links

        def clean_links(links):
            """
            Clean links which require login or sign up and containing
            some search/meta data parameters
            """
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
            """
            Validate address using geolocation API, first to make sure
            scraped address is a valid one, seccond to fix if there
            is any missing pieces and third to aid mt current task
            """
            if geo_key:

                r = requests.get(f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={geo_key}&searchtext={adr}')

                try:
                    location = json.loads(r.text)['Response']['View'][0]['Result']
                    return location[0]['Location']['Address']

                except Exception:
                    return None
            else:
                return adr

        def extend_addresses(address, geo_key=None):
            """
            If address is a valid one break up address to corresponding
            pieces (i.e. house number, street number, etc)
            """

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
                        if key == 'Country' and address[key] is not None:
                            c = define_country(address['Country'])
                            adr_dict['country'] = c
                            continue
                        adr_dict[key] = address[key]
            except Exception:
                adr_dict = None

            return adr_dict

        if self.model['address'] is not None and len(self.model['address']) > 0:
            if extend_addresses(self.model['address'], self.geo_key) is not None:
                extended = extend_addresses(self.model['address'], self.geo_key)
                for key, val in extended.items():
                    if key.lower() == 'country' and self.model['country']:
                        continue
                    self.model[key.lower()] = val

        else:
            self.model['address'] = None

        if self.model['address']:
            if len(self.model['address']) > 25:
                self.model['address'] = None

    def fix_link(self, link):
        """
        requests library does not handle well links in www.site.com format,
        hence needs to be fixed to be the format 'https://www.site.com'
        """
        if link.startswith('www.'):
            return 'https://'+link
        return link

    def split_phones(self):
        """
        Method to seperate found phones into individual ones
        """
        if self.split_phones_to_cols:
            for i in range(6):
                try:
                    if self.model['phones'][i].startswith('+'):
                        self.model[f'phone_{i+1}'] = self.model['phones'][i]
                        continue
                    self.model[f'phone_{i+1}'] = self.model['phones'][i]
                except IndexError:
                    pass

    def scrape_text(self, method):
        """
        Scrape text of the page of interest;
        credit for the module scrape_policy_text
        goes to Olha Babich
        """

        for key, _ in internal_links.items():
            if self.model[key] is not None:
                if 'contact' in key:
                    continue
                text_key = key.split('_')[0]+'_text'
                text_list = _get_text_list(self.model[key], method=method, web_driver=self.driver)
                self.model[text_key] = text_list
                try:
                    if self.model[text_key] is not None:
                        if self.model['company_name'] is not None:
                            text = ' '.join(text_generator(text_mas=self.model[text_key][0], 
                                                company_name=self.model['company_name'],
                                                company_website=self.model['url']))
                            self.model[text_key] = text
                        else:
                            text = ' '.join(text_generator(text_mas=self.model[text_key][0], 
                                                company_name='Company',
                                                company_website=self.model['url']))
                            self.model[text_key] = text
                except TypeError:
                    self.model[key] = None

            try:
                assert len(self.model[text_key]) > 1
                if self.model[text_key][0] is None \
                and self.model[text_key][1] is None:
                    self.model[text_key] = None
            except Exception:
                pass

    def remove_not_parsed(self):
        """
        Common issue is incapability to render the JavaScript whcih
        results in the text like 'Seems your browser is not using
        JavaScript...'
        """
        fields = ['faq_text', 'privacy_text', 'return_text', 
                'shipping_text', 'terms_text', 'warranty_text']

        for each in fields:
            if self.model[each] is not None:
                if 'JavaScript' in self.model[each]:
                    self.model[each] = None

    def scrape(self):
        """
        General pipeline of methods to scrape the website
        """
        self.soup = self.get_soup(self.url)
        if self.soup is None:
            return
        self.init_model()
        self.logging()
        self.define_domain()
        if self.model['company_name'] is None:
            self.get_name()
        self.find_address()
        self.find_phones()
        self.find_email()
        self.find_links()

        if self.model['address'] is not None \
        or len(self.model['address']) != 0:
            self.validate_address()

        if self.model['contact_link']:
            self.soup = self.get_soup(self.model['contact_link'])
        if self.soup is None:
            return
        if self.model['address'] is None or len(self.model['address']) == 0:
            self.find_address()
            self.validate_address()
        self.find_phones()
        if self.model['email'] is None or len(self.model['email']) == 0:
            self.find_email()
        if self.method == 'requests':
            self.scrape_text(method='requests')
        else:
            self.scrape_text(method='webdriver')

        self.remove_not_parsed()

        if self.model['phones']:
            fixed_phones = []
            for phone in list(self.model['phones']):
                ph = process_phones(phone, self.model['country'])
                fixed_phones.append(ph)

            self.model['phones'] = fixed_phones
        else:
            self.model['phones'] = None

        if self.model['phones']:
            self.split_phones_to_cols = True
            self.split_phones()

        if self.verbose == 1:
            for key, val in self.model.items():
                print(key, ':', val)

        if self.driver:
            self.driver.quit()

        return self.model