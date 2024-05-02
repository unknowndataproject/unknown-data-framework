'''
In this module
first apply the heuristic input
then search for dataset mention
and if not found apply NLp model

The model first copy a list of 10 pdfs to its local directory and work on them and when it is does it remove them and copy another until it hanldes all pdfs.
'''
import json
import os
import shutil
from pathlib import Path

import utils
import heurstics_search as hs
import using_nlp_model as unlp
from time import perf_counter

# Copy the entire directory tree from source to destination
# directory_path = Path('/data/mentions/in_pdfs')
# directory_path.mkdir()



'''
shutil.copytree("./resources/data/in_pdfs", "../../data/mentions/in_pdfs",dirs_exist_ok=True)

directory_path = Path('../../data/mentions/out_tei')
directory_path.mkdir(exist_ok=True)

directory_path = Path('../../data/mentions/results')
directory_path.mkdir(exist_ok=True)



#load cofig dictionary
config = utils.read_config("local_config.yaml")
#create logger
log_printer = utils.get_logger(config.log_file)
'''

def file_exists(file_path):
    path = Path(file_path)
    return path.is_file()

# load cofig dictionary
config = utils.read_config("local_config.yaml")
# create logger
log_printer = utils.get_logger(config.log_file)

batch_size = config.grobid_batch_size
pdf_list = os.listdir(config.pdf_dir)
destination_dir = config.grobid_pdf_dir

processed_tei_files_list = []
all_extration_results = []
for i in range(0, len(pdf_list), batch_size):  # math.ceil(len(pdf_list)/batch_size)+1):

    log_printer(f"****************************Handling Batch {i} *****************************")
    # take a batch of 10 pdfs
    pdf_batch = pdf_list[i:i + batch_size]

    for file_name in pdf_batch:
        # source_path = os.path.join(source_dir,file_name)
        # destination_path = os.path.join(destination_dir, os.path.basename(file_name))


        source_path = Path(f"{config.pdf_dir}/{file_name}")
        destination_path = Path(f"{destination_dir}/{file_name}")

        if file_exists(source_path):
            print('yes')

        shutil.copy(source_path, destination_path)
