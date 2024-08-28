'''
In this module
first apply the heuristic input
then apply NLp model

The model first copy a list of 10 pdfs to its local directory and work on them and when it is does it remove them and copy another until it hanldes all pdfs.
'''
import json
import os
import shutil
from pathlib import Path

import utils
import heurstics_search as hs
import using_nlp_model as unlp


def main():
    print("Start mentions-pdf")
    config = init()

    print("Create tei files")
    utils.convert_pdf_to_tei(config)

    print("Extract sentences")
    tei_dict = get_sentences(config.tei_dir)

    print("Select relevant sentences")
    heu_selected_sents = select_relevant_sentences(tei_dict)

    print("Prepare Sentences")
    nlp_input = prepare_sentences(tei_dict, heu_selected_sents)

    print("Apply NLP Model")
    all_extration_results = apply_model_to_sentences(nlp_input, config)

    print("Write Export")
    # Write the list of objects to the JSON file
    with open(config.results_in_json, "w") as json_file:
        json.dump(all_extration_results, json_file, indent=4)


def init():
    shutil.copytree("/app/src/resources/data/in_pdfs", "/data/mentions/in_pdfs", dirs_exist_ok=True)

    directory_path = Path('/data/mentions/out_tei')
    directory_path.mkdir(exist_ok=True)

    directory_path = Path('/data/mentions/results')
    directory_path.mkdir(exist_ok=True)

    config = utils.read_config("config.yaml")
    
    return config


def get_sentences(tei_directory: str) -> dict:
    """
    Returns list of sentences for each teil file in given directory
    """
    tei_dict = {}
    for tei_file in os.listdir(tei_directory):
        if str(tei_file)[-7:] != "tei.xml":
            continue

        full_path = os.path.join(tei_directory, tei_file)
        sentences = utils.get_sentences(full_path)

        tei_dict[str(tei_file)]= sentences
    return tei_dict


def select_relevant_sentences(tei_dict: dict):
    """
    apply heuristics and select setences
    """
    heu_selected_sents = {}
    for tei_file,sentences in tei_dict.items():
        _, matched_sent_ids = hs.search_patterns_in_tei_file(sentences)
        heu_selected_sents[tei_file] = matched_sent_ids
    return heu_selected_sents


def prepare_sentences(tei_dict: dict, heu_selected_sents:dict):
    """
    prepare sentences for nlp model
    """
    nlp_input = {}
    for tei_file,sentences in tei_dict.items():
        candidate_sentences = heu_selected_sents[tei_file]
        tmp_nlp_sents = []
        #create a new list of sentences that excludes the one to which a pattern is matched
        for sent in sentences:
            if sent['idx'] in candidate_sentences:
                tmp_nlp_sents.append(sent)
        nlp_input[tei_file] = tmp_nlp_sents
    return nlp_input


def apply_model_to_sentences(nlp_input, config):
    all_extration_results = []
    for tei_file,sentences in nlp_input.items():
        #skip files that do not have sentences selected by the heuristic
        if len(sentences)==0:
            continue
        
        try:
            file_path = f"{config.extraction_dir}/{tei_file[:-8]}.txt"

            file = open(file_path,"w",encoding="utf-8")

            for sentence in sentences:
                # this dictionary will contain all
                file_extraction_result = {}

                context = sentence['text']

                #skip short contexts
                if len(context)< config.short_context_length:
                    continue

                #enable impossbile answers if the number of candidate sentences is less than a specific threshold
                strict_extractor = False if len(sentences) < config.strict_threshold else True
                prediction = unlp.get_model_preds_on_one_sentence(sentence['text'],strict_extraction=strict_extractor)
                if prediction['start'] != prediction['end']:
                    #add extaction output to a dictionary
                    file_extraction_result["mentioned_in_paper"] = tei_file
                    file_extraction_result["context_id"] = sentence["idx"]
                    file_extraction_result["dataset_context"]=sentence["text"]
                    file_extraction_result["mention_start"]=prediction["start"]
                    file_extraction_result["mention_end"] = prediction["end"]
                    #add the dictionary to the list of all results to be saved in json
                    all_extration_results.append(file_extraction_result)
                    
                    file.write("\n{},{},{},{}\n".format(sentence["idx"],sentence["text"],prediction["start"],prediction["end"]))
        except Exception as e:
            print(e)

    return all_extration_results


if __name__ == '__main__':
    main()