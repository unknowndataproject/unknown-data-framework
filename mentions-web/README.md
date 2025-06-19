# Mentions Web

This component is responsible for extracting dataset mentions from the text. The text here consists of sentences extracted from web pages obtained from the crawler component.

## Overview 

This extraction component involves four steps:

1. Extract sentences from webpages, each stored as a WARC record in a WARC file obtained using the crawler.

2. Select English sentences and remove sentences in other languages.

3. Use heuristic rules to select sentences that might contain dataset mentions based on a set of keywords.

4. Employ DeBERTa in question-answering mode, as detailed in this [paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10231147), to carry out the actual extraction of the candidate sentences passed from step 2.

## Setup 

Here are some of the parameters that can be changed:

- The heuristic rules that are used to filter the sentences in step 3 can be modified in module `"main_mentions-web.py"`

- The question to be used in DeBERTa can be changed in module `"mentions-web/src/using_nlp_model.py"`

