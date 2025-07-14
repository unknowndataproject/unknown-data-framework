# Mentions PDF

This component is responsible for extracting dataset mentions from the text. The text here consists of sentences extracted from scientific papers in PDF format.
## Overview 

This extraction component involves three steps:

1. Extract sentences from PDFs using GROBID.

2. Use heuristic rules to select sentences that might contain dataset mentions based on a set of keywords.

3. Employ DeBERTa in question-answering mode, as detailed in this [paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10231147), to carry out the actual extraction of the candidate sentences passed from step 2.


## Setup 

Here are some of the parameters that can be changed:

- The heuristic rules that are used to filter the sentences in step 2 can be modified in module `"heurstics_search.py"`

- The question to be used in DeBERTa can be changed in module `"mentions-pdf/src/using_nlp_model.py"`
