'''
This module contains the Heurestics suggested by Lu to selects the sentences that has dataset mentions, references or urls.
'''

import re
from tqdm import tqdm


from colorama import Fore, Style
import traceback


def print_in_red(text, start, end):
    print(text[:start], end='')
    print(Fore.RED+text[start:end],end='')
    print(Style.RESET_ALL+text[end:])
    return

def keyword_matching(pattern_str, text):
    pattern = re.compile(pattern_str)
    match_iterator = pattern.finditer(text)
    res = []
    for match in match_iterator:
        if match:
            res.append(match)
            # print(match.group(), match.span())
    return res

# extract reference info from sentences
def extract_ref(sent_obj):
    if len(sent_obj['annotations']) == 0:
        return []
    res = []
    for _anno in sent_obj['annotations']:
        if _anno['type'] == 'ReferenceToBib':
            if 'target' in _anno:
                res.append((_anno['begin'], _anno['end'], _anno['target']))
            else:
                res.append((_anno['begin'], _anno['end'], ''))
    return res


def search_pattern_in_tei_file(sents, pattern, save_to=None):
    list_of_sents=[]
    matched_sentence_indexes = set()
    try:
        for sent in sents:
            refs = extract_ref(sent)
            #if len(refs) > 0:
                #print(refs)
            res = keyword_matching(pattern, sent['text'])
            if len(res) > 0:
                first_match = res[0]
                start, end = first_match.span()
                #sentence id, sentence text, dataset mention, start, end
                print(sent['text'])
                list_of_sents.append((sent['idx'],sent['text'], sent['text'][start:end+1],start, end))
                matched_sentence_indexes.add(sent['idx'])
    except Exception as e:
        print('error: ', e)
        traceback.print_tb(e.__traceback__)

    return list_of_sents, matched_sentence_indexes


def search_patterns_in_tei_file(sentences):
    pattern_results = []
    matched_sentence_indexes = set() #this list saves the sentences indexes to which a match have been found
    patterns = ['(?i)benchmark(?:s|)', '(?i)data(?:\s|)set(?:s|)', '(?i)survey', '(?i)questionnaire']
    for pattern in tqdm(patterns,total=len(patterns),desc="Matching Patterns"):
        pattern_matched_sentences, pattern_matched_sent_idx = search_pattern_in_tei_file(sentences,pattern)
        if len(pattern_matched_sentences)>0:
            pattern_results.extend(pattern_matched_sentences)
            matched_sentence_indexes.update(pattern_matched_sent_idx)

    return pattern_results, matched_sentence_indexes




'''
def run_on_tei_dir(tei_path, pattern, save_to=None):
    tei_files = list(Path(tei_path).iterdir())
    num_files = len(tei_files)
    print(num_files)

    list_of_sents = []
    try:
        for i in range(num_files):  # num_files
            tei_file = list(Path(tei_path).iterdir())[i]
            if str(tei_file)[-3:] == 'txt':
                continue
            doc_text, annos = transform_xml(tei_file, sentences=True)
            sents = get_ents('Sentence', doc_text, annos)
            print(tei_file)
            sents = list(sents)
            # if i==0:
            #     print(sents[:10])
            for j, sent in enumerate(sents):
                # if len(sent['annotations']) > 0:
                #     print(sent['annotations'])
                # print(i,j, _tmp['type'])
                refs = extract_ref(sent)
                if len(refs) > 0:
                    print(refs)
                res = keyword_matching(pattern, sent['text'])
                if len(res) > 0:
                    first_match = res[0]
                    start, end = first_match.span()
                    # list_of_sents.append([i,j, highlight_in_red(sent['text'], start, end)])
                    list_of_sents.append([i, j, sent['text'], start, end])
    except Exception as e:
        print('error: ', e)
        traceback.print_tb(e.__traceback__)

    if type(save_to) == str:
        with open(save_to, 'w') as fw:
            for line in list_of_sents:
                if type(line) == str:
                    continue
                fw.write('|||'.join([str(e) for e in line]))
                fw.write('\n')

    return list_of_sents


start = perf_counter()

tei_path = 'resources/out_tei/'
patterns = ['(?i)benchmark(?:s|)','(?i)data(?:\s|)set(?:s|)']
pattern = '(?i)data(?:\s|)set(?:s|)'
list_of_sents = run_on_tei_dir(tei_path, pattern)

print(len(list_of_sents))

for xx in list_of_sents:
    print_in_red(xx[2],xx[3],xx[4])

stop = perf_counter()

print(stop-start)
'''
