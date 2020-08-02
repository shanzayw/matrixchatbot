from bs4 import BeautifulSoup   #scraping by using the BeautifulSoup package

import requests

import sys

sys.path.append("./../")

from services.database_service import (add_data_basis_entry, add_new_domain,
    check_if_domain_already_in_data_basis, delete_existing_data_basis)
from nlp import language_processing

#index is used for the data basis; topics need to be transfered into db
#topics are identified by the 'li' tag or the 'a' tag

#later method with parameter url
#def add_data_basis(module, url, url_prefix):
#url = url_prefix + url

def list_to_string(topic):
    output = ""
    for i in range(0, len(topic)):
        output = output + str(topic[i]) + " "
    return output

def add_second_index():
    module = "Chatbots"
    module_original = module
    module = module.lower()

    module_in_db = check_if_domain_already_in_data_basis(module)

    if module_in_db == None:

        #url = "https://oer.gitlab.io/OS/index-terms.html"
        #url_prefix = "https://oer.gitlab.io/OS/"
        #response = requests.get(url)
        #response =
        soup = BeautifulSoup(open("test_index.html"), "html.parser")
        links = soup.findAll('li')
        numberOfLinks = len(links)
        module_id = add_new_domain(module, module_original, url)
        for link in links:

            ul = link.find('ul')

            if ul != None:    #this is a topic within the index without a link, get fist upcoming link then

                topic = ul.find_previous('li').text
                topic_original = topic.partition('\n')[0]
                topic = language_processing(topic_original)[1]
                topic = list_to_string(topic)
                url = ul.find('a').get('href')    #first link is taken

            else:

                topic_original = link.find('a').text
                topic = language_processing(topic_original)[1]   #get final message of nlp module
                topic = list_to_string(topic)
                url = link.find('a').get('href')

            add_data_basis_entry(module_id, topic_original, topic, url)

def add_data_basis():

    module = "Operating Systems (OS)"
    module_original = module
    module = module.lower()
    module_in_db = check_if_domain_already_in_data_basis(module)

    if module_in_db == None:

        url = "https://oer.gitlab.io/OS/index-terms.html"
        url_prefix = "https://oer.gitlab.io/OS/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text)
        links = soup.findAll('li')
        numberOfLinks = len(links)
        module_id = add_new_domain(module, module_original, url)
        for link in links:

            ul = link.find('ul')

            if ul != None:    #this is a topic within the index without a link, get fist upcoming link then

                topic = ul.find_previous('li').text
                topic_original = topic.partition('\n')[0]
                topic = language_processing(topic_original)[1]
                topic = list_to_string(topic)

                url = ul.find('a').get('href')    #first link is taken
                url = url_prefix + url

            else:

                topic_original = link.find('a').text
                print("Added topic: " + str(topic_original))
                topic = language_processing(topic_original)[1]   #get final message of nlp module
                topic = list_to_string(topic)
                url = link.find('a').get('href')
                url = url_prefix + url

            add_data_basis_entry(module_id, topic_original, topic, url)

def delete_existing_data_basis(module):
    module = module.lower()
    delete_existing_data_basis(module)


if __name__ == '__main__':
    add_data_basis()
    #add_second_index()     #remove the # if you want to
