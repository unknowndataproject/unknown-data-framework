# Export

An example use case how the created dataset can be used. 
It identifies the most used hosts of datasets based on the previously gathered data. 

## Overview 

This model uses the output of the coreference model to identify hosts of datasets. The hosts are descendinly ordered by the number of detected related datasets. The results are exported into a csv file that contains as colums the link to the host, the number of related identified datasets, and five links to datasets from that host.

## Setup 

Currently, the output of the coreference model is used that is based on the PDF mentions component. To switch this to the web mentions component, simple update the INPUT_FILE constant in the `relevant-hosts.py` file. 