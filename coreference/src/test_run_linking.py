from entity_linking import dataset_linking
from database_access import read_dataset_metadata_from_file
import json
import os
from pprint import pprint


def read_json(filepath):
    with open(filepath, 'r') as fr:
        d = json.load(fr)
    return d

def read_extraction_csv(filepath):
    with open(filepath, 'r') as fr:
        lines = fr.readlines()
        lines = [line for line in lines if line != '' and line != '\n']
    for line in lines:
        line = line.split(',')
    return lines

def read_tsv2dict(filepath):
    res_dict = {}
    with open(filepath, 'r') as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip().split('\t')
            res_dict[line[0]] = line[1]
    return res_dict

def run_test_entity_linking():
    dataset_mention_metadata_dir = '/data/mentions/' 
    pdf_mention_file = 'pdfs_extraction.json'

    dataset_mention_metadata_file = '/app/data/sample3_dataset_mention_metadata.json'
    paper_id_mapping_file = '/app/data/sample_3_paper_id_mapping.tsv'
    extra_dataset_metadata_file = '/app/data/matched_dataset_paper_metadata.json'
    # for f in os.listdir(dataset_mention_metadata_dir):
    #     if os.path.isfile(os.path.join(dataset_mention_metadata_dir, f)):
    #         extraction_res = read_extract_csv(os.path.join(dataset_mention_metadata_dir, f))
    all_mentions_metadata = read_json(dataset_mention_metadata_file)
    all_mentions_metdata = read_json(os.path.join(dataset_mention_metadata_dir, pdf_mention_file))
    extraction_res = all_mentions_metadata[:200]
    # print(len(extraction_res))
    metadata_db = read_dataset_metadata_from_file('/app/data/datasets.json.gz')
    extra_metadata_db = read_json(extra_dataset_metadata_file)
    extra_metadata_dict = { e['dataset_name']: {k: v if not k =='paper_authors' else [{'author_name': author} for author in v] for k,v in e.items()} for e in extra_metadata_db}

    linked_res = dataset_linking(extraction_res, metadata_db)
    paper_id_mapping = read_tsv2dict(paper_id_mapping_file)
    # print(paper_id_mapping) 
    linked_res = {k: {kk:vv if not kk=='mentioned_in_paper' else paper_id_mapping[vv] for kk, vv in v.items()} for k,v in linked_res.items()}
    
    for k,v in linked_res.items():
        dataset_name = v['dataset_entity']
        if dataset_name in extra_metadata_dict:
            _metadata = extra_metadata_dict[dataset_name]
            linked_res[k]['dataset_author'] = _metadata["paper_authors"]
            linked_res[k]['source_paper'] = {k:v for k,v in _metadata.items() if 'paper' in k}
            linked_res[k]['dataset_introduced_date'] = _metadata['paper_date']
            linked_res[k]['metadata_creator'] = 'UnknownData'
            linked_res[k]['metadata_external_source'] = ['PapersWithCode Data Dump']
    with open('/data/coreference/pdf_output.json', 'w') as fw:
        json.dump(linked_res, fw, indent=4)
    return linked_res

# print(os.getcwd())
# print(os.listdir(os.getcwd()))
run_test_entity_linking()
