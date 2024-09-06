import os
import gzip
import json
from pprint import pprint
import pandas as pd
import logging



def read_dataset_metadata_from_file(filepath, encoding='ascii'):
    """
    paperswithcode provides the following metadata field for dataset:
    url, name, fullname, homepage, description, paper, introduced_date, warning, modalities, tasks, languages, variants, num_papers, data_loaders
    """
    with gzip.open(filepath, 'rb') as frb:
        d = json.loads(frb.read().decode(encoding))
        # pprint(d[0].keys())
        num_field = len(d[0])
        # print(len(set(d[0].keys()) - set(d[1].keys()))))
        for i, e in enumerate(d):
            if len(e) != num_field or (len(set(e.keys()) - set(d[0].keys())) != 0):
                print(i, 'Not all fields are shared by the entries.')
       #  print('Finish inspection.')
    # pprint(d[:3])
    df = pd.DataFrame.from_records(d)
    # pprint(df.head())
    return df


def read_gesis_dataset_json_gz(filepath, encoding='utf-8'):
    with gzip.open(filepath, 'r') as fin:
        data = json.loads(fin.read().decode(encoding))
    
    data = data['hits']['hits']
    # print(data[0].keys())
    # print(data[0]['_source'].keys())
    data = [{'_id': record['_id']} | {k:v for k,v in record['_source'].items() if k in ['doi','title_info', 'locations', 'content_info']} for record in data]
    # print(data[0])
    return data

# read_dataset_metadata_from_file('./data/datasets.json.gz')
