# credit: Olha Babich, Data Scientist at WiserBrand

# changelog by Valentyna Fihurska
#
# added option to use requests library for 
# function _get_text_list i.e. user can choose
# whether to use webdriver or requests

from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import re
from nltk import tokenize
import random
import requests

key_words_dict = {'privacy_policy': ['privacy policy', 'privacy'],
                  'return_policy': ['return'],
                  'warranty': ['warranty'],
                  'faq': ['faq', 'frequently asked questions'],
                  'shipping': ['shipping', 'delivery'],
                  'terms and conditions': ['terms']
                  }


def _clean_base_url(url):
    try:
        url_pattern = re.compile(r"http(?:s)?://(?:[-._a-zA-Z0-9])+")
        cleaned_url = re.findall(pattern=url_pattern, string=url)[0]
        return cleaned_url
    except Exception as e:
        print('Error in _clean_base_url({})'.format(url), e)


def _prepare_url(url):
    try:
        to_replace = ['https://', 'http://', 'www.']
        for el in to_replace:
            if el in url:
                url = url.replace(el, '')
        return url
    except Exception as e:
        print('Error in _prepare_url({})'.format(url), e)


def _is_same_domain(checked_url, received_url):
    prepared_checked_url = _prepare_url(checked_url)
    prepared_received_url = _prepare_url(received_url)
    if prepared_checked_url in prepared_received_url or prepared_received_url in prepared_checked_url:
        return True
    else:
        return False


def _clean_target_url(url):
    if len(url) > 0:
        url_pattern = re.compile(r"http[s]?://(?:[#._a-zA-Z0-9\/\-])+")
        res = re.findall(pattern=url_pattern, string=url)
        if len(res) > 0:
            cleaned_url = re.findall(pattern=url_pattern, string=url)[0]
            if cleaned_url[-1] == '/':
                cleaned_url = cleaned_url[:-1]
            return cleaned_url
        else:
            return None
    else:
        return None


def _create_link_from_href(href_attr, base_url, skip_words):
    try:
        stop_counter = 0
        for word in skip_words:
            if word in href_attr:
                stop_counter += 1
        if stop_counter > 0:
            return None
        if len(href_attr) < 1:
            return None
        prepared_base_url = _prepare_url(base_url)

        if 'http' in href_attr and not _is_same_domain(prepared_base_url, href_attr):
            return None

        if prepared_base_url in href_attr:
            if href_attr[0] != '/':
                target_link = href_attr
            elif len(href_attr) > 2:
                if href_attr[:2] == '//':
                    target_link = 'https:' + href_attr

        elif href_attr[0] == '/':
            target_link = base_url + href_attr
        else:
            target_link = base_url + '/' + href_attr

        if target_link[-1] == '#':
            return None
        return target_link
    except Exception as e:
        return None



def _get_links_list(web_driver, url_to_scrape):
    try:
        web_driver.implicitly_wait(30)
        url_to_scrape = _clean_base_url(url_to_scrape)
        web_driver.get(url_to_scrape)
        soup = BeautifulSoup(web_driver.page_source, 'lxml')
        link_list = soup.findAll('a')
        if len(link_list) > 0:
            link_list = link_list[::-1]

        return link_list, url_to_scrape
    except Exception as e:

        return None, None


def _select_best_link(keyword, link_mas, key_words_dict):
    np_link_mas = np.array(link_mas)
    unique_links, unique_link_indexes = np.unique(np_link_mas[:, 1], return_index=True)
    if len(unique_links) == 1:
        return unique_links[0]
    else:
        unique_link_mas = np_link_mas[unique_link_indexes, :]
        sorted_mas = sorted(unique_link_mas[:, ], key=lambda x: len(x[0].split()))
        return sorted_mas[0][1]


def _analyze_parameter_part(link, key, key_dict):
    link_mas = link.split('?')
    base_part, option_part = link_mas[0], link_mas[1]
    if '&' in option_part:
        option_part_mas = option_part.split('&')
    base_part_counter = 0
    option_part_counter = 0
    for word in key_dict[key]:
        if word in base_part.lower():
            base_part_counter += 1

        if word in option_part.lower():
            option_part_counter += 1
    if '.jsp' in base_part:
        return link
    if base_part_counter > 0:
        return base_part
    if 'utm' in option_part:
        return base_part
    if option_part_counter > 0 or (base_part_counter == 0 and option_part_counter == 0):
        return link


def get_text(link, options, company_name, company_website):
    """
    функция для выкачивания текста по одной ссылке
    :param company_website:
    :param link: ссылка на страницу с полисис
    :param options: параметры для хромдрайвера
    :return:
    """
    if link is not None and type(link) == str and len(link) > 0:
        driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
        res, url = _get_text_list(driver, link)
        if res is not None:
            company_website = company_website.replace('https://', '').replace('http://', '')
            if company_website.find('/') > -1:
                company_website = company_website[:company_website.find('/')]
            b = text_generator(res, company_name, company_website)
            if b is not None:
                driver.quit()
                return ' '.join(b)
            else:
                driver.quit()
                return None
        else:
            driver.quit()
            return None


phone_numbers_pattern = re.compile('([\+\(\)\-\. 0-9]{7,23})')
date_pattern = re.compile(
    '(?:[A-Za-z]{3,9} [0-9]{1,2}, [0-9]{4})|(?:[0-9]{1,2}[.\/-]?[0-9]{1,2}[.\/-]?[0-9]{2,4})|(?:[0-9]{1,2}[:\-]{1}[0-9]{1,2})')
symbol_pattern = re.compile('[#%$><}{]{1}')
url_pattern = re.compile(r'[A-Za-z0-9]+([\-\.]{1}[A-Za-z0-9]+)*\.[\/A_Z0-9a-z]+')


def text_generator(text_mas, company_name, company_website):
    patterns_to_skip = [phone_numbers_pattern,
                        date_pattern,
                        symbol_pattern]  # ,  url_pattern]
    temp = []

    for el in text_mas:

        if el.name == 'p':
            text_tmp = []
            for tag in el.contents:
                if tag.name is not None and tag.name != 'a':
                    temp_content = tag.contents
                    for t in temp_content:
                        if t.name is not None and t.name != 'a' and t.contents is not None:
                            temp_content2 = t.contents
                            if len(temp_content2) == 0:
                                continue
                            elif temp_content2[0].name is None:
                                text_tmp.append(str(temp_content2[0]))
                        else:
                            text_tmp.append(str(t))
                else:
                    text_tmp.append(str(tag))
            text = '\n'.join(text_tmp)

        else:
            text = el.text.strip()

        if text is not None and len(text) > 0:

            if '..' in text:
                continue

            if '\n' in text:
                text_splitted = text.split('\n')

                for par in text_splitted:
                    if len(par.split()) >= 4:
                        temp.append(par)
            elif len(text.split()) >= 4:
                temp.append(text)

    temp2 = []
    for el in temp:

        sentences = tokenize.sent_tokenize(el)

        for sen in sentences[:]:

            sen = sen.strip()
            if sen in temp2:
                continue

            if len(sen.split()) < 3:
                continue

            if re.match('[A-Z]', sen[0]) is None or sen[-1] != '.':
                continue

            if 'cart' in sen.lower() or 'registration' in sen.lower() or 'invalid' in sen.lower() or 'get' in sen.lower() or 'please select' in sen.lower() or 'enter' in sen.lower() or 'cookie' in sen.lower() or 'shopping bag' in sen.lower() or 'search result' in sen.lower() or 'click' in sen.lower() or 'see here' in sen.lower() or 'please see' in sen.lower():
                continue

            counter = 0
            for pattern in patterns_to_skip:
                if len(re.findall(pattern=pattern, string=sen.lower())) > 0:
                    counter += 1
            if counter > 0:
                continue

            replace_characters = {'“': '"', '’': "'", '”': '"', '–': '-', '®': '', '\xa0': ' '}
            for key in replace_characters:
                sen = sen.replace(key, replace_characters[key])
            sen = sen.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').strip()

            temp2.append(sen)

    if len(temp2) < 5 or len(' '.join(temp2)) < 800:
        return ''

    mas_length = len(temp2)
    curr_length = 5
    text_length = len(' '.join(temp2[:curr_length]))

    while text_length < 800 and curr_length <= mas_length:
        curr_length += 1
        text_length = len(' '.join(temp2[:curr_length]))

    word_pattern = '(?:[\W\"\(]{{1}}|^)({})(?:[\W\"\)\(\.\,;]{{1,3}}?|$)'
    pronoun_dict = {
        16:{re.compile(word_pattern.format("I")): ['The Company', company_name, company_website, 'Website']},
        15:{re.compile(word_pattern.format("my")): ["Company's", company_name + "'s'"]},
        14:{re.compile(word_pattern.format("mine")): ["Company's", company_name + "'s'"]},
        12: {re.compile(word_pattern.format('us')): ['The Company', company_name, company_website, 'Website']},
        13: {re.compile(word_pattern.format('we')): ['The Company', company_name, company_website, 'Website']},
        10: {re.compile(word_pattern.format('you')): ['The Client', 'The Customer', 'The User',
                                                      'The Client of {}'.format(company_name), 'The User of Website',
                                                      'The User of company services']},
        9: {re.compile(word_pattern.format('your')): ["The Client's", "The Customer's", "The User's"]},
        11: {re.compile(word_pattern.format('our')): ["Company's", company_name + "'s'"]},
        0: {re.compile(word_pattern.format("we'd")): ['The company would', '{} would'.format(company_name),
                                                      '{} would'.format(company_website), 'website would']},
        1: {re.compile(word_pattern.format("we'll")): ['The company will', '{} will'.format(company_name),
                                                       '{} will'.format(company_website), 'website will']},
        2: {re.compile(word_pattern.format("we're")): ['The company is', '{} is'.format(company_name),
                                                       '{} is'.format(company_website), 'website is']},
        3: {re.compile(word_pattern.format("we've")): ['The company has', '{} has'.format(company_name),
                                                       '{} has'.format(company_website), 'website has']},
        4: {re.compile(word_pattern.format("you'd")): ['The client would', 'The customer would', 'User would',
                                                       'the client of the {} would'.format(company_name),
                                                       'the user of website would',
                                                       'the user of company services would']},
        5: {re.compile(word_pattern.format("ours")): ['The Company', company_name, company_website, 'Website']},
        7: {re.compile(word_pattern.format("yours")): ['The Client', 'The Customer', 'The User',
                                                       'The Client of {}'.format(company_name), 'The User of Website',
                                                       'The User of company services']},
        6: {re.compile(word_pattern.format("yourself")): ['The Client', 'The Customer', 'The User',
                                                          'The Client of {}'.format(company_name),
                                                          'The User of Website', 'The User of company services']},
        8: {re.compile(word_pattern.format("you're")): ['The client is', 'The customer is', 'User is',
                                                        'The client of the {} is'.format(company_name),
                                                        'The user of website is', 'The user of company services is']}}

    if text_length >= 800:
        for i in range(curr_length):
            temp2[i] = pronoun_replacer(temp2[i], pronoun_dict)
        return temp2[:curr_length]
    else:
        return ''



def pronoun_replacer(sentence, to_replace_dict):
    is_upper = sentence.isupper()
    sentence_mas = sentence.split()

    if is_upper:
        for i in range(len(sentence_mas)):
            for num in range(14):
                for el in to_replace_dict[num].keys():

                    if re.search(el, sentence_mas[i].lower()) is not None:
                        word_mas = to_replace_dict[num][el]
                        index = random.choice(range(len(word_mas)))
                        new_word = word_mas[index]

                        while new_word in sentence_mas:
                            word_mas = word_mas[:index] + word_mas[index + 1:]
                            if len(word_mas) < 1:
                                break
                            index = random.choice(range(len(word_mas)))
                            new_word = word_mas[index]

                        sentence_mas[i] = re.sub(el, new_word, sentence_mas[i].lower()).upper()


    else:
        for i in range(len(sentence_mas)):
            for num in range(14):
                for el in to_replace_dict[num].keys():

                    if re.search(el, sentence_mas[i].lower()) is not None:
                        word_mas = to_replace_dict[num][el]
                        index = random.choice(range(len(word_mas)))
                        new_word = word_mas[index]

                        while new_word in sentence_mas:
                            word_mas = word_mas[:index] + word_mas[index + 1:]
                            if len(word_mas) < 1:
                                break
                            index = random.choice(range(len(word_mas)))
                            new_word = word_mas[index]

                        sentence_mas[i] = re.sub(el, new_word, sentence_mas[i].lower())
    #

    return ' '.join(sentence_mas)


def _get_text_list(url_to_scrape, method='requests', web_driver=None):
    """
    Получаем список тегов со странички, в которых скорее всего есть текст
    :param web_driver:
    :param url_to_scrape:
    :return:
    """
    try:
        if method == 'webdriver':
            web_driver.get(url_to_scrape)
            soup = BeautifulSoup(web_driver.page_source, 'lxml')
        else:
            r = requests.get(url_to_scrape)
            soup = BeautifulSoup(r.text, 'lxml')
        link_list = soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'span', 'li', 'br'])
        res = []
        tag_exceptions = {
            'div': ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'span', 'li', 'div', 'img', 'br', 'iframe', 'input', 'i'],
            'li': ['a', 'img', 'i'],
            'span': ['a', 'img', 'i', 'br'],
            'p': ['button']}
        for el in link_list:
            if el.name in tag_exceptions:
                if len(el.findAll(tag_exceptions[el.name])) > 0:
                    continue

            if el.parent in res:
                continue

            if 0 < len(el.contents) < 5:
                res.append(el)
        if len(res) == 0:
            link_list = soup.findAll(['div'])
            for el in link_list:
                if el.name in tag_exceptions:
                    if len(el.findAll(tag_exceptions[el.name])) > 0:
                        continue

                if 0 < len(el.contents) < 5:

                    res.append(el)

        return res, url_to_scrape

    except Exception as e:
        print(e)

        return None, None


def link_scraper(web_driver, options, url_to_scrape, company_name, key_words_dict, skip_words):
    """
    Функция для вытаскивание ссылок и текстов всех доступных полисис
    :param web_driver:
    :param options:
    :param url_to_scrape:
    :param company_name:
    :param key_words_dict:
    :param skip_words:
    :return:
    """
    link_dict = dict()

    res, base_url = _get_links_list(web_driver, url_to_scrape)
    link_dict['base_url'] = base_url

    if res is not None:
        real_url = web_driver.current_url
        real_url = _clean_base_url(real_url)

        if not _is_same_domain(base_url, real_url):
            return None

        for el in res:
            # take elements with href attr
            if 'href' not in el.attrs:
                continue

            target_text = el.text.lower()
            if len(target_text) > 50:
                continue
            target_link = _create_link_from_href(el.attrs['href'], real_url, skip_words)

            if target_link is None:
                continue

            for key in key_words_dict:

                if key == 'help' and 'faq' in target_link.lower():
                    continue

                for key_word in key_words_dict[key]:
                    if key_word in target_text:

                        if '?' in target_link:
                            target_link = _analyze_parameter_part(target_link, key, key_words_dict)

                        if link_dict.get(key) is None:
                            link_dict[key] = [[target_text, target_link]]
                        elif link_dict.get(key) is not None and [target_text, target_link] not in link_dict.get(key):
                            link_dict[key].append([target_text, target_link])
        policy_textes = []
        result = dict()
        for key in link_dict:
            if key == 'base_url':
                continue
            if len(link_dict[key]) > 1:
                result[key + '_url'] = _select_best_link(key, link_dict[key], key_words_dict)
                text = get_text(result[key + '_url'], options, company_name, link_dict['base_url'])

                if text is not None:

                    if len(policy_textes) > 0:
                        similar = []
                        for el in policy_textes:
                            ratio = SequenceMatcher(None, el, text).ratio()
                            similar.append(ratio)

                        if max(similar) < 0.1:

                            result[key] = text
                            policy_textes.append(text)
                        else:
                            result[key] = ''
                    else:
                        result[key] = text
                        policy_textes.append(text)
                else:
                    result[key] = ''


            else:
                result[key + '_url'] = link_dict[key][0][1]

                text = get_text(result[key + '_url'], options, company_name, link_dict['base_url'])

                if text is not None:
                    if len(policy_textes) > 0:
                        similar = []
                        for el in policy_textes:
                            ratio = SequenceMatcher(None, el, text).ratio()
                            similar.append(ratio)

                        if max(similar) < 0.1:

                            result[key] = text
                            policy_textes.append(text)
                        else:
                            result[key] = ''
                    else:
                        result[key] = text
                        policy_textes.append(text)
                else:
                    result[key] = ''

        if len(result) > 0:
            result['base_url'] = link_dict['base_url']
            return result
        else:
            return None
    else:
        return None
