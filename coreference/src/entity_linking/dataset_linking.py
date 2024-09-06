import pandas as pd
from pprint import pprint
import spacy

nlp = spacy.load('en_core_web_md')


def dataset_linking(extraction_input, dataset_df): 
    """
    extraction input is a list of records of extracted dataset metadata:
    - dataset_context: str, the sentence context of dataset_mention
    - mention_start, mention_end: int, int, the starting and ending positions of mention substring in context
    - URL_in_context (optional): (URL_text, URL_start, URL_end) 
    - citation_in_context (optional): (reference_string, reference_start, reference_end)
    - mentioned_in_paper: paper_id 
    """
    # match dataset name
    try:
        cnt = 0 
        res = {}
        missed = {}
        mis_cnt = 0
        for ee in extraction_input:
            matched = False
            # get mention info
            mention_start, mention_end = ee['mention_start'], ee['mention_end']
            dataset_mention = ee['dataset_context'][mention_start:mention_end]
            dataset_mention = dataset_mention.strip()
            # pprint(dataset_mention)
            candid_ents = []
            
            for idx, dataset in dataset_df.iterrows():
                # get dataset info
                dataset_name, dataset_homepage, dataset_date = dataset['name'], dataset['homepage'], dataset['introduced_date']

                if dataset_name == dataset_mention: 
                    candid_ents.append({'name': dataset_name, 'homepage': dataset_homepage, 'score': 1.0})
                    break
                if dataset_name.lower() in dataset_mention.lower():
                    score = nlp(dataset_name.lower()).similarity(nlp(dataset_mention.lower()))
                    # print('score: ', score)
                    candid_ents.append({'name':dataset_name, 'homepage': dataset_homepage, 'score': score})
                elif dataset_mention.lower() in dataset_name.lower():
                    score = nlp(dataset_name.lower()).similarity(nlp(dataset_mention.lower()))
                    print('Dataset name: ', dataset_name, ', score: ', score)
                    # candid_ents.append({'name':dataset_name, 'homepage': dataset_homepage, 'score': score})
                else:
                    pass
                    # print(f'No match: {dataset_name} ||| {dataset_mention}')
                    
            
            # rank and match 
            if len(candid_ents) > 0:
                sorted_candid_ents = sorted(candid_ents,key=lambda x: x['score'], reverse=True) 
                dataset_name, dataset_homepage, score = sorted_candid_ents[0]['name'], sorted_candid_ents[0]['homepage'], sorted_candid_ents[0]['score']
                if score > 0.5:
                    matched = True
                    cnt += 1
                    # print('Found a match {}:\n\tEntity from database: {}\n\tMatched mention: {}\n\tContext: {}'.format(score, dataset_name, dataset_mention, ee['dataset_context']))
                    res[cnt] = {
                    'dataset_entity':dataset_name, 
                    'dataset_homepage': dataset_homepage,
                    'dataset_author': '',
                    'dataset_introduced_date': dataset_date,
                    'matched_mention': dataset_mention, 
                    'matched_context': ee['dataset_context'],
                    'mentioned_in_paper': ee['mentioned_in_paper'], 
                    }
            if not matched:
                # print('Miss a mention:', dataset_mention,'\nContext:', ee['dataset_context'], '\n')
                missed[mis_cnt] = {'missed_mention': dataset_mention}
                mis_cnt += 1
                pass

        # print(cnt)
        return res, missed
    except Exception as e:
        raise e
    # match dataset URL

