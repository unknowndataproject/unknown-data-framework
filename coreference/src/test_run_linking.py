from entity_linking import dataset_linking
from database_access import read_dataset_metadata_from_file
import json
import os
from pprint import pprint


def read_dataset_extraction_results(filepath):
    with open(filepath, 'r') as fr:
        d = json.load(fr)
    return d


def run_test_entity_linking():
    extraction_res = read_dataset_extraction_results('./src/data/sample3_dataset_mention_metadata.json')
    metadata_db = read_dataset_metadata_from_file('./src/data/datasets.json.gz')
    # print(metadata_db[metadata_db['name'].str.contains('validation|Validation')].name)
    # print(metadata_db[metadata_db.name.str.contains('ShanghaiTech')][['name', 'description']].to_string())
    # print('External metadata entry count: ', len(metadata_db), '\nExtraction input count is', len(extraction_res))
    linked_res = dataset_linking(extraction_res, metadata_db)
    with open('/data/coreference/test_output.json', 'w') as fw:
        json.dump(linked_res, fw, indent=4)
    return linked_res

# print(os.getcwd())
# print(os.listdir(os.getcwd()))
run_test_entity_linking()
