from entity_linking import dataset_linking
from database_access import read_dataset_metadata_from_file, read_gesis_dataset_json_gz
import gzip
import json
from pathlib import Path
from pprint import pprint


def read_json(filepath):
    with open(filepath, 'r') as fr:
        d = json.load(fr)
    return d


def read_json_gz(filepath, encoding='utf-8'):
    with gzip.open(filepath, 'r') as fin:
        data = json.loads(fin.read().decode(encoding))
    return data

def read_jsonl_gz(filepath):
    res = []
    with gzip.open(filepath, 'rb') as fr:
        json_list = list(fr)
        for e in json_list:
            d = json.loads(e)
            res.append(d)
    return res


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
    ## read dataset mention from WP3
    dataset_mention_metadata_dir = '/data/mentions/' 
    pdf_mention_file = 'pdfs_extraction.json'

    dataset_mention_metadata_file = '/app/data/sample3_dataset_mention_metadata.json'
    paper_id_mapping_file = '/app/data/sample_3_paper_id_mapping.tsv'
    extra_dataset_metadata_file = '/app/data/matched_dataset_paper_metadata.json'
    gesis_dataset_metadata_file = '/app/data/gesis_search_datasets_19042024.json.gz'
    # for f in os.listdir(dataset_mention_metadata_dir):
    #     if os.path.isfile(os.path.join(dataset_mention_metadata_dir, f)):
    #         extraction_res = read_extract_csv(os.path.join(dataset_mention_metadata_dir, f))
    # all_mentions_metadata = read_json(dataset_mention_metadata_file)
    
    """
    Link to pdf mentions
    """
    print('Start entity linking for mentions from PDF')
    all_mentions_metadata = read_json(Path(dataset_mention_metadata_dir).joinpath(pdf_mention_file))
    extraction_res = all_mentions_metadata[:]
    metadata_db = read_dataset_metadata_from_file('/app/data/datasets.json.gz')
    extra_metadata_db = read_json(extra_dataset_metadata_file)
    extra_metadata_dict = { e['dataset_name']: {k: v if not k =='paper_authors' else [{'author_name': author} for author in v] for k,v in e.items()} for e in extra_metadata_db}
    gesis_db = read_gesis_dataset_json_gz(gesis_dataset_metadata_file, encoding='utf-8')
    # pprint(gesis_db[:3])
    linked_res, missed_mentions_pdf = dataset_linking(extraction_res, [gesis_db, metadata_db])
    paper_id_mapping = read_tsv2dict(paper_id_mapping_file)
    linked_res = {k: {kk:vv if not kk=='mentioned_in_paper'  else vv for kk, vv in v.items()} for k,v in linked_res.items()}
    
    for k,v in linked_res.items():
        dataset_name = v['dataset_entity']
        if dataset_name in extra_metadata_dict:
            _metadata = extra_metadata_dict[dataset_name]
            linked_res[k]['dataset_author'] = _metadata["paper_authors"]
            linked_res[k]['source_paper'] = {k:v for k,v in _metadata.items() if 'paper' in k}
            linked_res[k]['dataset_introduced_date'] = _metadata['paper_date']
            linked_res[k]['metadata_creator'] = 'UnknownData'
            linked_res[k]['metadata_external_source'] = ['PapersWithCode Data Dump']
    print('Finish linking and output results to pdf_output.json')
    print(len(linked_res))
    with open('/data/coreference/pdf_output.json', 'w') as fw:
        json.dump(linked_res, fw, indent=4)


    """
    Link to web mentions
    """
    print('Start entity linking for mentions from web pages')
    web_mention_file = 'web-mentions/00000.gz'
    web_mention_metadata = read_jsonl_gz(Path(dataset_mention_metadata_dir).joinpath(web_mention_file))
    # pprint(web_mention_metadata)
    formated_web_mention_metadata = []
    for e in web_mention_metadata:
        for m in e['matches']:
            formated_web_mention_metadata.append({'mentioned_in_paper': e['uri'], 
                                       'dataset_context': m[0],
                                       'mention_start': m[-2], 
                                       'mention_end': m[-1]})
    # pprint(formated_web_mention_metadata)
    linked_web_res, missed_mentions_web = dataset_linking(formated_web_mention_metadata, [gesis_db, metadata_db])
    # pprint(missed_mentions_web)
    print(len(linked_web_res))
    print('Finish entity linking and output results to web_output.json')
    with open('/data/coreference/web_output.json', 'w') as fw:
        json.dump(linked_web_res, fw, indent=4)
    return linked_res

run_test_entity_linking()
