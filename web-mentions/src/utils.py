import json
import sys

import yaml
import re
from bs4 import BeautifulSoup


#define a dictionary to store config files
class AttDict(dict):
    def __init__(self,*args,**kwargs):
        super(AttDict,self).__init__(*args,**kwargs)
        self.__dict__ = self

#read the config file and return it as dictionary
def read_config(config_file):
    return AttDict(yaml.load(open(config_file,"r"),Loader = yaml.FullLoader))



# Function to get the complete path of a tag in the DOM tree
def get_dom_path(tag):
    parent = tag.parent
    path = [tag.name]
    while parent and parent.name != '[document]':
        path.insert(0, parent.name)
        parent = parent.parent
    return ' > '.join(path)

# Function to recursively traverse the DOM tree and extract text
def extract_text(tag, min_word_count):
    text_dict = {}
    for child in tag.children:
        if child.name:
            if child.name != 'script':  # Exclude script tags
                text = child.text.strip()
                if len(text.split()) >= min_word_count:  # Check if text contains at least min_word_count words
                    path = get_dom_path(child)
                    text_dict[path]=text
            text_dict.update(extract_text(child, min_word_count))
    return text_dict

#this function receives a webpage html as a string along with short context to consider
def extract_text_from_html(html_content,short_context_length):
    print(html_content)
    soup = BeautifulSoup(html_content, 'lxml' )#'html.parser')

    # Find the body tag
    body_tag = soup.find('body')

    # Extract text starting from the body tag
    if body_tag:
        text_dict = extract_text(body_tag,short_context_length)
        #text_string = '\n'.join(text_lines)
        print(text_dict)
    else:
        print("Body tag not found in the HTML content.")

    #text_content = soup.get_text(separator='\n', strip=True)
    return text_dict

# Function to save dictionary to JSON file
def save_dict_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


#this function saves a string or a list to a text file
def save_to_text_file(data, filename):
    if isinstance(data, str):
        with open(filename, 'w', encoding='utf-8') as output_file:
            output_file.write(data)
    elif isinstance(data, list):
        with open(filename, 'w', encoding='utf-8') as output_file:
            for item in data:
                if isinstance(item, tuple):
                    line = ' '.join(str(elem) for elem in item)
                    output_file.write(line + '\n')
                else:
                    raise ValueError("Each element of the list must be a tuple")
    else:
        raise ValueError("Input data must be a string or a list")

'''



# Function to get the complete path of a tag in the DOM tree
def get_dom_path(tag):
    parent = tag.parent
    path = [tag.name]
    while parent and parent.name != '[document]':
        path.insert(0, parent.name)
        parent = parent.parent
    return ' > '.join(path)

# Function to recursively traverse the DOM tree and print text along with their paths
def extract_texts_and_paths(tag):
    text_list = []
    for child in tag.children:
        if child.name:
            if child.name != 'script':  # Exclude script tags
                text_list.append(f"{get_dom_path(child)}: {child.text.strip()}")
            text_list.extend(extract_texts_and_paths(child))
    return text_list
    


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml' )#'html.parser')

    # Find the body tag
    body_tag = soup.find('body')

    # Extract text starting from the body tag
    if body_tag:
        text_lines = extract_texts_and_paths(body_tag)
        text_string = '\n'.join(text_lines)
        print(text_string)
    else:
        print("Body tag not found in the HTML content.")

    sys.exit(0)
    #text_content = soup.get_text(separator='\n', strip=True)
    return text_content


'''




