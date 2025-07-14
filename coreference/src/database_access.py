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
    pprint(data[0])
    print(data[0]['_source'].keys())
    data = [{'_id': record['_id']} | {k:v for k,v in record['_source'].items() if k in ['doi','title_info', 'locations', 'collection_info','content_info', 'date']} for record in data]
    print(data[0]['date'])
    mapped_data = []
    for e in data:
        _e = {}
        for k,v in e.items():
            try:
                if k == 'title_info':
                    _e["dataset_name"] = v["title"]
                elif k == "content_info":
                    if "content" in v: 
                        _e["description"] = v["content"]
                    elif "content_de" in v:
                        _e["description"] = v["content_de"]
                elif k == "doi":
                    _e["homepage"] = "https:/doi.org/" + v
                elif k == "date":
                    if "pub_date" in v:
                        _e["introduced_date"] = v["pub_date"]
                    else:
                        _e["introduced_date"] = None
                    _v = {kk:vv for kk,vv in v.items() if kk != "pub_date"}
                    if len(_v) > 0:
                        _e['date'] = _v
                elif k == "collection_info":
                    if "collection" in v:
                        _e["collection"] = v["collection"]
                    else:
                        _e["collection"] = v["collection_de"]
            except KeyError as e:
                print(v)
                raise e
        mapped_data.append(_e)

    return mapped_data

# read_dataset_metadata_from_file('./data/datasets.json.gz')
