import os
from pathlib import Path

from warcio.archiveiterator import ArchiveIterator

import utils

#this function receives a directory that has warc files and loop throw them to extract the webpages they contain
def handel_warc_files(warc_dir,html_dir,text_dir):
    for warc_file in os.listdir(warc_dir):
        warc_file_path = os.path.join(warc_dir, warc_file)
        cur_html_dir = html_dir+warc_file[:-8]
        cur_text_dir = text_dir+warc_file[:-8]

        # Check if the cur_html_dir exists, and create it if not
        if not os.path.exists(cur_html_dir):
            os.makedirs(cur_html_dir,exist_ok=True)

        if not os.path.exists(cur_text_dir):
            os.makedirs(cur_html_dir,exist_ok=True)

        #hadle warc file
        extract_webpages_from_warc(warc_file_path,cur_html_dir,cur_text_dir)


#this function extracts html pages from a warc file and stores them in seperate file. Also extract their text and store them in json files
def extract_webpages_from_warc(warc_file_path, html_dir,text_dir):
    with open(warc_file_path, 'rb') as warc_file:
        file_list = []
        i=0
        for record in ArchiveIterator(warc_file):
            if record.rec_type == 'response' and record.http_headers.get_header('Content-Type', '').startswith('text/html'):
                warc_target_uri = record.rec_headers.get_header('WARC-Target-URI')
                warc_record_id = record.rec_headers.get_header('WARC-Record-ID')
                try:
                    webpage_content = record.content_stream().read().decode('utf-8',errors='replace')
                    # Try to decode as UTF-8, replacing errors
                    #webpage_content = content_bytes.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    # Handle decoding errors gracefully
                    print(f"Error decoding {warc_target_uri}. Skipping...")
                    continue

                file_list.append((i,warc_record_id,warc_target_uri))

                # save html source
                html_file_path = f"{html_dir}/{i}.txt"
                utils.save_to_text_file(webpage_content,html_file_path)

                # Extract text content from HTML in dictionary format,
                # key is path in DOM and value is text
                text_dict = utils.extract_text_from_html(webpage_content,config.short_context_length)

                # save text_dict in json format
                utils.save_dict_to_json(text_dict, f"{text_dir}/{i}.json")

                i+=1
    utils.save_to_text_file(file_list,f"{config.web_mentions}+{warc_file_path.split('/')[-1]}_results.txt")


#load cofig dictionary
config = utils.read_config("config.yaml")

if __name__ == "__main__":
    #create web mentions output directory
    directory_path = Path(config.web_mentions)
    directory_path.mkdir(exist_ok=True)

    handel_warc_files(config.warc_dir,config.extracted_html_dir,config.extracted_text_dir)

    #extract_mentions_from_webpages(config)


