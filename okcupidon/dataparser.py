from urllib.request import urlretrieve

from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from urllib.parse import urlunparse


def mod_pic_url(src):
    url = urlparse(src)
    path_parts = url.path.split('/')
    path_parts[4] = path_parts[7]
    path_parts[5] = path_parts[7]
    path_parts[6] = path_parts[7]
    return str(urlunparse((url.scheme, url.hostname, '/'.join(path_parts), None, '', '')))

def save_profile_images(profile_id, soup):
    for profile_thumb_div in soup.find_all('div', {'class': 'profile-thumb'}):
        i = 0
        for img in profile_thumb_div.find_all('img'):
            src = ""
            if img.has_attr('data-src'):
                src = img['data-src']
            elif img.has_attr('src'):
                src = img['src']
            else:
                print('Empty src or data-src tag for ' + profile_id)

            if src != '':
                try:
                    outpath = 'images/' + profile_id + '/'
                    os.makedirs(outpath, exist_ok=True)
                    urlretrieve(mod_pic_url(src), outpath + str(i) + ".jpg")
                    i = i + 1
                except Exception as e:
                    print(e)




def parse_profile(profile_id, html_page):
    """This function parses the html page, looking for profile data and returns a dict """
    soup = BeautifulSoup(html_page, "html.parser")

    save_profile_images(profile_id, soup)

    data_structure = {
        'age': ['span', {'class': 'profile-basics-asl-age'}],
        'location': ['span', {'class': 'profile-basics-asl-location'}],
        'essays': {'category': ['h2', {'class': 'profile-essay-category'}],
                   'title': ['h2', {'class': 'profile-essay-title'}],
                   'contents': ['p', {'class': 'profile-essay-contents'}]
                   },
        'details': {'basic': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--basics'}],
                    'badge': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--black-lives-matter'}],
                    'pronoun': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--pronouns'}],
                    'looks': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--looks'}],
                    'background': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--background'}],
                    'lifestyle': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--lifestyle'}],
                    'family': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--family'}],
                    'wiw': ['div', {
                        'class': 'matchprofile-details-section matchprofile-details-section--wiw'}],
                    }
    }
    parsed_data = {}

    # Basic info - id
    parsed_data['id'] = profile_id

    # Basic info - age
    parsed_data['age'] = soup.find_all(
        data_structure.get('age')[0],
        data_structure.get('age')[1])[0].text

    # Basic info - location
    parsed_data['location'] = soup.find_all(
        data_structure.get('location')[0],
        data_structure.get('location')[1])[0].text

    # Essays
    parsed_data['essays'] = list()
    for box in soup.find_all('div', {'class': 'profile-essay'}):
        box_essay = {}
        box_essay['category'] = box.find_all(
            data_structure['essays'].get('category')[0],
            data_structure['essays'].get('category')[1])[0].text

        box_essay['title'] = box.find_all(
            data_structure['essays'].get('title')[0],
            data_structure['essays'].get('title')[1])[0].text

        try :
            box_essay['contents'] = box.find_all(
                data_structure['essays'].get('contents')[0],
                data_structure['essays'].get('contents')[1])[0].text
        except IndexError :
            box_essay['contents'] = 'NaN'

        parsed_data['essays'].append(box_essay)

    # Details column
    parsed_data['details'] = {}
    for section in soup.find_all('div', {'class': 'quickmatch-profiledetails matchprofile-details'}):
        for detail in data_structure['details'].keys():

            element = data_structure['details'][detail][0]
            css_class = data_structure['details'][detail][1]['class']

            if section.find(element, css_class):
                parsed_data['details'][detail] = section.find(element, css_class).\
                find('div', 'matchprofile-details-text').text


    return parsed_data
