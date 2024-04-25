'''
This module loads a given output from the coreference module
and creates an output file that can be used to integrate the data 
into the dblp services.
'''

import shutil
import json
from datetime import datetime
from lxml import etree


INPUT_FILE = '/data/coreference/pdf_output.json'
OUTPUT_FILE = f'/data/dblp-export/unknown-data-framework_dblp-export_{datetime.now().isoformat()}.tp'

DOCTYPE = '<!DOCTYPE tp SYSTEM "tp.dtd">'
PUBLISHER = 'UnknownData Project'


def main():
    publications = load_dataset_publications()
    tp = create_tp_document(publications)
    write_tp_file(tp)
    copy_dtd_file()


def load_dataset_publications():
    with open(INPUT_FILE) as file:
        publications = json.load(file)
    return publications


def create_tp_document(publications):
    tp = etree.Element('tp')
    tp.set('debug', 'false')

    set_history_element(tp)

    generic = etree.SubElement(tp, 'generic',attrib={'type':'data'})
    publisher = etree.SubElement(generic, 'publisher')
    publisher.text = PUBLISHER

    toc = etree.SubElement(generic, 'toc')

    for publication in publications[:100]: # TODO Split data into handleable chunks
        toc.append(generate_publication_element(publication))

    return tp


def set_history_element(tp):
    metadata = etree.SubElement(tp, 'metadata')
    history = etree.SubElement(metadata, 'history')
    log = etree.SubElement(history, 'log')
    log.set('timestamp', str(datetime.now()))
    log.set('source', 'unknown-data-framework')


def generate_publication_element(item):
    title = item['dataset_name']
    homepage = item['dataset_homepage']
    authors = item['paper_authors']
    year = 9999 # TODO add actual data
    type = 'dataset'

    publication = etree.Element('publication')
    publication.set('type', type)

    for author in authors:
        authorElement = etree.SubElement(publication, 'author')
        nameElement = etree.SubElement(authorElement, 'name')
        nameElement.set('native', author)
        nameElement.text = author
    
    titleElement = etree.SubElement(publication, 'title')
    titleElement.text = title

    yearElement = etree.SubElement(publication, 'year')
    yearElement.text = f'{year}'

    urlElement = etree.SubElement(publication, 'url')
    urlElement.text = homepage

    return publication


def write_tp_file(xml):
    tree = etree.ElementTree(xml)

    with open(OUTPUT_FILE, "wb") as file:
        file.write(etree.tostring(tree, 
                        pretty_print=True, 
                        xml_declaration=True, 
                        encoding='utf-8',
                        doctype=DOCTYPE))
        

def copy_dtd_file():
    shutil.copyfile("./files/tp.dtd", "/data/dblp-export/tp.dtd")


if __name__ == '__main__':
    main()