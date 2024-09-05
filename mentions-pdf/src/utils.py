''' This module contains the code needed to use grobid, sentence extraction from tei and other program
wide functionality like logging etc..'''

import os
from pathlib import Path

import shutil

from colorama import Fore,Style
import yaml


#pdf handling packages
from grobid_client.grobid_client import GrobidClient

#flaten code
from flattentei.tei_to_text_and_standoff import transform_xml
from flattentei.extract_parts import get_ents

import pandas as pd


def convert_pdf_to_tei(config):
    print("Start to convert files")
    client = GrobidClient(config_path=config.grobid_config)#"grobid_client_python/config.json")

    client.process("processFulltextDocument", config.pdf_dir, output=config.tei_dir,
                   consolidate_citations=True, tei_coordinates=False, force=True, segment_sentences=True, n=config.grobid_batch_size)


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

