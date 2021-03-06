import sys

sys.path.append("./../")

from services.database_service import add_organisation_entry, get_domain_description_id
from nlp import language_processing

'''
analyze simple text documents and store rules into data basis of db
text document consists of topic + response
'''

def add_organisation_document():
    '''adds an organisation document, adjust filepath accordingly'''
    module = "Syllabus"    #add belonging module name here
    module = module.lower()

    document_name = "../knowledge_domains/organisation.txt"  #filepath

    module_id = get_domain_description_id(module)
    if module_id != None:
        with open(document_name, "r") as file:
            for line in file:
                line = line.rstrip("\n")
                elements = line.split(':')
                topic = elements[0]
                response = elements[1]
                response = response.strip()
                evaluate_topic(module, topic, response)

def evaluate_topic(module, topic, response):
    '''adds additional rules for data basis'''
    original = "Organisational"
    formulations = []
    if topic == 'Modulname':
        module = response
    if topic == 'Klausurtermin':
        formulations = ['Klausurtermin', 'Wann Klausur', 'Termin der Klausur']
    if topic == 'Klausurdauer':
        formulations = ['Klausurdauer', 'Wie lange dauert Klausur',]
    if topic == 'Klausurzulassung':
        formulations = ['Klausurzulassung', 'Wie wird Klausur zugelassen']
    if topic == 'Vorlesungstermine':
        formulations = ['Vorlesungstermine', 'Wann Vorlesung', 'Termine Modul', "Wann Vorlesungen"]
    if topic == 'Vorlesungskonzept':
        formulations = ['Vorlesungskonzept', 'Welches Konzept', 'Welches Vorlesungskonzept']
    if topic == 'Dozenten':
        formulations = ['Dozenten', 'Dozent', 'Welche Dozenten']
    if topic == 'Lehrmaterialien':
        formulations = ['Lehrmaterialien', 'Wo Lernmaterialien', 'Wo Vorlesungsfolien']
    if topic == 'Abgaben':
        formulations = ['Abgaben', 'Gibt Abgaben', 'Pflichtabgaben']
    if topic == 'Pr??sentationen':
        formulations = ['Pr??sentationen', 'Wo Pr??sentationen']
    if topic == 'Sonstiges zum Modul':
        formulations = ['Sonstiges zum Modul', 'Sonstige Informationen']
    if topic == 'Exam date':
        formulations = ['Exam date', 'When exam', 'What exam date']
    if topic == 'Exam duration':
        formulations = ['Exam duration', 'how long exam', 'time will exam take']
    if topic == 'Exam approval':
        formulations = ['Exam approval', 'how exam approval']
    if topic == 'Lecture dates':
        formulations = ['Lecture dates', 'when lectures', 'what lecture dates']
    if topic == 'Lecture concept':
        formulations = ['Lecture concept', 'which lecture concept']
    if topic == 'Lecturers':
        formulations = ['Lecturers', 'who holds presentations']
    if topic == 'Teaching materials':
        formulations = ['Teaching materials', 'where teaching materials']
    if topic == 'Duties':
        formulations = ['Duties', 'course duties', 'regular exercises']
    if topic == 'Presentations':
        formulations = ['Presentations', 'where can presentations be found']
    if topic == 'Other information about the module':
        formulations = ['Other information about the module', 'more information about module']
    for i in range(0, len(formulations)):
        current = formulations[i]
        processed = language_processing(current)
        after_lemmitation = processed[3]  #take nlp result of after lemmitation, since small talk contains stop words
        after_lemmitation = list_to_string(after_lemmitation)
        add_organisation_entry(module, original, after_lemmitation, response)

def list_to_string(message):
    '''method that transforms a list into a string'''
    final = ""
    for i in range(0, len(message)):
        final = final + message[i] +  " "
    return final

if __name__ == '__main__':
    add_organisation_document()
