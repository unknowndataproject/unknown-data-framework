import os
from pathlib import Path
import csv
import re
import json
import gzip
import time

from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

import fastwarc.stream_io as fws
import fastwarc.warc as fww
import resiliparse.extract.html2text as rpe
from resiliparse.parse.lang import detect_fast as detect_lang

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


def fast_extract_webpages_from_warc(warc_file_path, output_directory):
    warc_dir = Path(warc_file_path)
    outpath = Path(output_directory)
    outpath.mkdir(parents=True, exist_ok=True)

    warc_files = warc_dir.glob('*.warc.gz')

    languages = ['at', 'be', 'bg', 'cy', 'cz', 'de', 'dk', 'ee', 'en', 'es', 'fi', 'fr', 'gr', 'hr', 'hu', 'ie', 'it', 'lt',
                 'lu', 'lv', 'mt', 'nl', 'pl', 'pt', 'ro', 'se', 'si', 'sk']

    rec_proc_count = 0
    rec_match_count = 0
    match_counter = 0
    for f in sorted(warc_files):
        outfile = outpath.joinpath(f.name.split('-')[2] + '.gz')
        print(f"processing: {f}")
        print(f"writing to: {outfile}")
        stream = fws.GZipStream(fws.FileStream(str(f), 'rb'))

        patterns = ['(?i)benchmark(?:s|)', '(?i)data(?:\s|)set(?:s|)', '(?i)survey', '(?i)questionnaire']
        patterns_re = [re.compile(pattern) for pattern in patterns]

        with gzip.open(outfile, 'wb') as of:
            for record in fww.ArchiveIterator(stream, record_types=fww.WarcRecordType.response, func_filter=fww.is_http):
                content = record.reader.read(record.content_length)
                rec_proc_count += 1
                # Warning: non utf-8 characters are removed
                content_text = rpe.extract_plain_text(str(content, 'utf-8', 'ignore'), main_content=True, alt_texts=True)
                if detect_lang(content_text, langs=languages)[0] == 'en':
                    record_data = {}
                    record_data['id'] = record.headers.get('WARC-Record-ID')
                    record_data['uri'] = record.headers.get('WARC-Target-URI')
                    record_data['file'] = record.headers.get('WARC-Filename')
                    record_data['matches'] = []
                    sentences = content_text.split('. ')
                    for sentence in sentences:
                        if len(sentence) > 30:
                            for pattern in patterns_re:
                                match_it = pattern.finditer(sentence)
                                for match in match_it:
                                    match_counter += 1
                                    record_data['matches'].append(sentence)
                    if len(record_data['matches']) > 0:
                        of.write(json.dumps(record_data).encode('utf-8'))
                        of.write("\n".encode('utf-8'))
                        rec_match_count += 1

    print(f"processed {rec_proc_count} records")
    print(f"saved {match_counter} matches out of {rec_match_count} records")


#load cofig dictionary
config = utils.read_config("config.yaml")


if __name__ == "__main__":
    #create web mentions output directory
    directory_path = Path(config.text_dir)
    directory_path.mkdir(exist_ok=True)

    #handel_warc_files(config.warc_dir,config.text_dir)
    start_time = time.time()
    fast_extract_webpages_from_warc(config.warc_dir, config.text_dir)
    print(f"finished in {time.time() - start_time} seconds")


