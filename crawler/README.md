# Crawler

This component crawls the web for mentions of datasets based on a seed list of URLs. 

## Overview 

The crawler component is based on the Internet Archive's web crawler project called Heritrix. Based on that system, it crawls the web by downloading pages, using broad heuristics to identify if the page may contain a mention of a dataset (e.g., the page contains a DOI or mentions the term *data set* in German, English, or French). If the heuristic is met, the page is locally stored. Furthermore, it will utilize found URLs on the pages (regardless of whether the page contains a dataset mention or not) to recursively search for pages that may contain a dataset mention. The tool uses a seed list stored at `crawler/src/seed.txt` as a starting point.

## Setup 

The crawler has two main areas where it can adjust its behavior. First, the URL seed list `crawler/src/seed.txt` can be adjusted to reflect the domain that should be searched for data set mentions. Second, the file `crawler/src/crawler-beands.cxml` defines the behavior of Heritrix, such as the depth at which it should follow URLs. More information on the configuration of Heritrix can be found [here](https://heritrix.readthedocs.io/en/latest/configuring-jobs.html). 
