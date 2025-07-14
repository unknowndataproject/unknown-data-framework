# Coreference

This component links the dataset mentions from PDF and the web output to two external dataset knowledge bases based on PapersWithCode dataset and GESIS Search dataset corpus.

## Overview 

The linking involves a score function calculation phase and a ranking and selection phase. For each of the dataset mention from a context, we either find a string string matching result with 1.0 matching score, or calculate the cosine similarity value as the matching score with each of the candidate dataset entity name. We rerank all the candidate dataset entities based on this matching score and pick the entity with a score above a minimum threshold and the highest value as the matched dataset entity for the dataset mention. For all the dataset mentions that can be matched based on this strategy, we output the results accordingly. 


