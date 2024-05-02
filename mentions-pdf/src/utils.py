''' This module contains the code needed to use grobid, sentence extraction from tei and other program
wide functionality like logging etc..'''

import os
from pathlib import Path

import shutil

from colorama import Fore,Style
import yaml


#pdf handling packages
from grobid_client_python.grobid_client import grobid_client
#from grobid_client.grobid_client import GrobidClient


#flaten code
from flattentei.tei_to_text_and_standoff import transform_xml
from flattentei.extract_parts import get_ents

import pandas as pd


def convert_pdf_to_tei(config):
    client = grobid_client.GrobidClient(config_path=config.grobid_config)#"grobid_client_python/config.json")
    client.process("processFulltextDocument", config.pdf_dir, output=config.tei_dir,
                   consolidate_citations=True, tei_coordinates=True, force=True, segment_sentences=True,n=config.grobid_batch_size)

    #client.process("processFulltextDocument", "./resources/in_pdfs", output="./resources/out_tei",
    #                   consolidate_citations=True, tei_coordinates=True, force=True, segment_sentences=True)


#this function takes a tei file name and returns a list of dictionary containing the sentences extracted from that file.
def get_sentences(tei_file):
    doc_text, annos = transform_xml(tei_file)

    sentences = get_ents("Sentence", doc_text, annos)
    sentences = list(sentences)

    return sentences

#define a dictionary to store config files
class AttDict(dict):
    def __init__(self,*args,**kwargs):
        super(AttDict,self).__init__(*args,**kwargs)
        self.__dict__ = self

#read the config file and return it as dictionary
def read_config(config_file):
    return AttDict(yaml.load(open(config_file,"r"),Loader = yaml.FullLoader))


#this function returns a logger that prints the mesage at console and save it in a log file
def get_logger(log_file):
    def print_log(message):
        #print(message,end="\n")
        with open(log_file,"a",encoding='utf-8') as f:
            f.write(message+"\n")
    return print_log

#this function text and color and print a specific section of the text in the given color
def text_highligher(text, start, end, color):
    color_code = getattr(Fore, color.upper(), None)
    if color_code is None:
        raise ValueError(f"Invalid color: {color}")

    print(text[:start], end='')
    print(color_code + text[start:end+1], end='')
    print(Style.RESET_ALL + text[end+1:])

def copy_pdf_files(file_list,source_dir, destination_dir):
    for file_name in file_list:
        source_path = Path(source_dir) / file_name
        destination_path = Path(destination_dir) / file_name

        try:
          shutil.copy(source_path, destination_path)
          #print(f"File '{source_path}' copied to '{destination_path}'")
        except FileNotFoundError:
          print(f"Error: File '{source_path}' not found.")
        except PermissionError:
          print(f"Error: Permission denied for '{destination_path}'.")


def delete_pdf_files(file_list,destination_dir):
    for file_name in file_list:
        try:
            file_path = os.path.join(destination_dir,file_name)
            os.remove(file_path)
            #print(f"File '{file_path}' deleted.")
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            print(f"Error: Permission denied for '{file_path}'.")