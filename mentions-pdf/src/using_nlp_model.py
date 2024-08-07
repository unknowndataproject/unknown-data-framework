import torch
from transformers import pipeline,AutoTokenizer,AutoModelForQuestionAnswering
from tqdm import tqdm
import re


exp=3
question = "On which data the study is based?"
# 4 "Which data samples or images are used"
# 3 "On which data the study is based"
# 2 "Which dataset or database is used?"
# 1 "Is there any use of data collected from a survey"
# 0 "What data are used?" #

model_checkpoint = "Yousef-Cot/dataset-mention-extractor"
local_model_folder= "/data/mentions/model"

device = 0 if torch.cuda.is_available() else -1

print(device)
print("*******************")

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint,cache_dir=local_model_folder)
model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint, cache_dir=local_model_folder)

pipe = pipeline("question-answering",model=model,tokenizer = tokenizer,padding=True, truncation=True,device=device)


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


def get_nlp_model_predictions(sentences):
    predicted_answers = []
    result_output = []
    for i,sentence in tqdm(sentences,desc="Using NLP model:"):
        predicted_ans = pipe(question=question,context=sentence)
        #predicted_ans2 = pipe(question=question,context=sample[2],handle_impossible_answer=True)
        tmp_new_row = []
        tmp_new_row.append(predicted_ans["answer"])
        #tmp_new_row.append(predicted_ans2["answer"])
        #print(tmp_new_row)
        result_output.append(tmp_new_row)
        #print("*****************************************")