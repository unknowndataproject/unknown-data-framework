import torch
from transformers import pipeline,AutoTokenizer,AutoModelForQuestionAnswering
from tqdm import tqdm
import re

import time

exp=3
question = "On which data the study is based?"
# 4 "Which data samples or images are used"
# 3 "On which data the study is based"
# 2 "Which dataset or database is used?"
# 1 "Is there any use of data collected from a survey"
# 0 "What data are used?" #

model_checkpoint = "Yousef-Cot/dataset-mention-extractor"  #f"src/resources/models/fold{exp}"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
pipe = pipeline("question-answering",model=model,tokenizer = tokenizer)


def get_model_preds_on_one_sentence(sentence,strict_extraction):
    predicted_ans = pipe(question=question, context=sentence,handle_impossible_answer=strict_extraction)
    if not strict_extraction:
        return post_process_prediction(predicted_ans)
    return predicted_ans

def post_process_prediction(model_output):
    #remove wods wich are all small letter
    answer = model_output['answer'].strip()

    if len(answer) < 3:
        model_output['start']=model_output['end']=0

    if len(answer) == 3:
        if answer in ['NER', 'NLP']:
            model_output['start']=model_output['end']=0
    #remove references
    pattern = r'\[(?:[1-9]|[1-9][0-9]|100)\]'
    match = re.search(pattern, answer)
    if match:
        model_output['start']=model_output['end']=0

    words = model_output['answer'].split()
    small_flag = all(word.islower() for word in words)
    if small_flag:
        model_output['start']=model_output['end']=0

    return model_output


def handle_matched_sentences(sentences,strict_threshold):
    # this list will contain all
    extraction_results = []

    for sent in sentences:
        # enable impossbile answers if the number of candidate sentences is less than a specific threshold
        strict_extractor = False if len(sentences) < strict_threshold else True

        prediction = get_model_preds_on_one_sentence(sent, strict_extraction=strict_extractor)

        if prediction['start'] != prediction['end']:
            extraction_results.append((sent,prediction['start'],prediction['end']))

    return extraction_results