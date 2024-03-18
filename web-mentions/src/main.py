import os
from pathlib import Path

from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

import utils

#this function receives a directory that has warc files and loop throw them to extract the webpages they contain
def handel_warc_files(warc_dir,html_dir):
    for warc_file in os.listdir(warc_dir):
        warc_file_path = os.path.join(warc_dir, warc_file)
        cur_html_dir = html_dir+warc_file[:-8]

        # Check if the cur_html_dir exists, and create it if not
        if not os.path.exists(cur_html_dir):
            os.makedirs(cur_html_dir)

        #hadle warc file
        extract_webpages_from_warc(warc_file_path,cur_html_dir)


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator='\n', strip=True)
    return text_content

#this function extracts html pages from a warc file and stores them in
def extract_webpages_from_warc(warc_file_path, output_directory):
    with open(warc_file_path, 'rb') as warc_file:
        file_list = []
        i=0
        for record in ArchiveIterator(warc_file):
            if record.rec_type == 'response' and record.http_headers.get_header('Content-Type', '').startswith('text/html'):
                url = record.rec_headers.get_header('WARC-Target-URI')
                try:
                    webpage_content = record.content_stream().read().decode('utf-8',errors='replace')
                    # Try to decode as UTF-8, replacing errors
                    #webpage_content = content_bytes.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    # Handle decoding errors gracefully
                    print(f"Error decoding {url}. Skipping...")
                    continue


                # Extract text content from HTML
                text_content = extract_text_from_html(webpage_content)


                # Save the HTML content to a file
                output_file_path = f"{output_directory}/{i}.txt"
                # add to list
                file_list.append((i, url))
                i +=1
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    #output_file.write(content)
                    output_file.write(text_content)

#load cofig dictionary
config = utils.read_config("config.yaml")


if __name__ == "__main__":
    #create web mentions output directory
    directory_path = Path(config.text_dir)
    directory_path.mkdir(exist_ok=True)

    handel_warc_files(config.warc_dir,config.text_dir)
