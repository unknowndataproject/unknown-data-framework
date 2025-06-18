'''
This modul uses the output of the coreference model to
identify the most used hosts. 
It returns an ordered list of the most used host together with
their number of occurences and some example links. 
The list is provided as CSV file.
'''

import json 
import csv
from urllib.parse import urlparse


INPUT_FILE = '/data/coreference/pdf_output.json'
OUTPUT_FILE = '/data/export/most-relevant-hosts.csv'


def main():
    data = load_coreference_output()
    hosts = extract_host_information(data)
    export_to_csv(hosts)


def load_coreference_output():
    with open(INPUT_FILE) as file:
        data = json.load(file)
    return data


def extract_host_information(data):
    'Returns list of used hosts, sorted descending by frequency, together with up to 5 example urls.'
    hosts = dict()
    for key, value in data.items():
        homepage = value['dataset_homepage']
        parsed = urlparse(homepage)
        host = f'{parsed.scheme}://{parsed.netloc}/'

        # Ignore empty homepages
        if not homepage.strip():
            continue

        if host not in hosts:
            hosts[host] = [homepage]
        else:
            hosts[host] += [homepage]

    result = []
    for key, value in hosts.items():
        result += [(key, len(value), value[:5])]

    result.sort(key=lambda x: x[1], reverse=True)
    return result


def export_to_csv(hosts):
    with open(OUTPUT_FILE, "w") as file:
        csv_file = csv.writer(file)
        csv_file.writerow(["host", "count", "examples"])
        csv_file.writerows(hosts)


if __name__ == "__main__":
    main()
