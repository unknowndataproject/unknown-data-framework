
'''
In this module
first apply the heuristic input
then search for dataset mention
and if not found apply NLp model

The model first copy a list of 10 pdfs to its local directory and work on them and when it is does it remove them and copy another until it hanldes all pdfs.
'''
import os
import shutil
from pathlib import Path

import utils
import heurstics_search as hs
import using_nlp_model as unlp
from time import perf_counter


# Copy the entire directory tree from source to destination
#directory_path = Path('/data/mentions/in_pdfs')
#directory_path.mkdir()


shutil.copytree("/app/src/resources/data/in_pdfs", "/data/mentions/in_pdfs",dirs_exist_ok=True)

directory_path = Path('/data/mentions/out_tei')
directory_path.mkdir(exist_ok=True)

directory_path = Path('/data/mentions/results')
directory_path.mkdir(exist_ok=True)



#load cofig dictionary
config = utils.read_config("config.yaml")
#create logger
log_printer = utils.get_logger(config.log_file)



batch_size = config.grobid_batch_size
pdf_list = os.listdir(config.pdf_dir)
destination_dir = config.grobid_pdf_dir

processed_tei_files_list = []
for i in range(0,len(pdf_list), batch_size): #math.ceil(len(pdf_list)/batch_size)+1):

    log_printer(f"****************************Handling Batch {i}*****************************")
    #take a batch of 10 pdfs
    pdf_batch = pdf_list[i:i+batch_size]
    
    #copy pdf patch into pdf_dir
    utils.copy_pdf_files(pdf_batch, config.pdf_dir,destination_dir)
    #print("batch copied\n")
    

    #convert all pdfs in the pdf direcotry to tei files and store them in tei_directory
    utils.convert_pdf_to_tei(config)

    #keys is tei file name, value is a list of sentences extracted from that dictionary
    tei_dict = {}
    #get sentences from tei files i
    for tei_file in os.listdir(config.tei_dir):
        #if the tei file is not processe it yet, add it to the list of processed files and process it
        if tei_file not in processed_tei_files_list:
            processed_tei_files_list.append(tei_file)
        else:#if the file is already processed, skip it
            continue
        #to hadle only tei files
        if str(tei_file)[-7:] != "tei.xml":
            log_printer(f"{tei_file} is not a tei file")
            continue

        #construc full path name to the tei file
        full_path = os.path.join(config.tei_dir, tei_file)

        #extract sentences from the tei file
        sentences = utils.get_sentences(full_path)

        #build a dictionary with tei_file as key and its sentences as
        tei_dict[str(tei_file)]= sentences

    #########################################################################################


    #apply heuristics and select setences
    #log_printer(f"Applying heuristics... \n")
    start_time = perf_counter()
    heu_results = {}
    heu_selected_sents = {}
    sent_excluded_by_heuristics = {}
    for tei_file,sentences in tei_dict.items():
        if tei_file  not in processed_tei_files_list:
            continue
        _, matched_sent_ids = hs.search_patterns_in_tei_file(sentences)
        heu_selected_sents[tei_file] = matched_sent_ids
    end_time = perf_counter()
    #log_printer(f"Applying heuristics took: {end_time-start_time}\n")
    #log_printer("***************************************\n")


    #prepare sentences for nlp model by
    nlp_input = {}
    for tei_file,sentences in tei_dict.items():
        if tei_file not in processed_tei_files_list:
            continue
        #load the sentences in which a heuristic pattern is found
        candidate_sentences = heu_selected_sents[tei_file]
        tmp_nlp_sents = []
        #create a new list of sentences that excludes the one to which a pattern is matched
        for sent in sentences:
            if sent['idx']  in candidate_sentences:
                tmp_nlp_sents.append(sent)
        nlp_input[tei_file]=tmp_nlp_sents

    #apply model on the sentences that was selected by heuristics
    nlp_results = {}
    for tei_file,sentences in nlp_input.items(): #tqdm(nlp_input.items(),total = len(nlp_input.items()), desc="processing: "):
        #skip files that do not have sentences selected by the heuristic
        if tei_file  not in processed_tei_files_list or len(sentences)==0:
            continue
        
        log_printer(f"Dataset mentions found in file: {tei_file[:-8]}.pdf\n")
        log_printer(f"Total number of sentences : {len(tei_dict[tei_file])}\n")
        #log_printer("Number of sentences per file for which a known dataset was matched: ")
        log_printer(f"Number of sentences selected by heuristics: {len(heu_selected_sents[tei_file])}\n")

        try:
            file_path = f"{config.extraction_dir}/{tei_file[:-8]}.txt"

            f = open(file_path,"w",encoding="utf-8")

            for sent in sentences:
                context = sent['text']

                #skip short contexts
                if len(context)< config.short_context_length:
                    continue

                #enable impossbile answers if the number of candidate sentences is less than a specific threshold
                strict_extractor = False if len(sentences) < config.strict_threshold else True
                prediction = unlp.get_model_preds_on_one_sentence(sent['text'],strict_extraction=strict_extractor)
                if prediction['start'] != prediction['end']:
                    utils.text_highligher(sent['text'],prediction['start'],prediction['end'],"RED")
                    f.write("\n{},{},{},{}\n".format(sent["idx"],sent["text"],prediction["start"],prediction["end"]))
                    log_printer("\n{},{},{},{},{}".format(tei_file,sent["idx"],sent["text"],prediction["start"],prediction["end"]))
            log_printer("\n********************************************\n")
            #print("\n****************************************************\n")
        except Exception as e:
            log_printer(e)

    #remove pdfs after handling them
    utils.delete_pdf_files(pdf_batch,destination_dir)
    #print("\nbatch files are deleted \n")

