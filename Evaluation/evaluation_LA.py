import sys
import os
import json
import csv
import re

from functools import lru_cache

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LA_evaluation import compute_recall_coverage, compute_cosine_similarity, lemmatize
from functions import preprocess, get_ngram, frequency_term_POS

@lru_cache(maxsize=None)
def lemmatize_cached(word: str) -> str:
    return lemmatize(word)

## Obtain the relevant information from the lexical profile 
def get_generated(filename, timeframe):
    dir = os.path.join(filename, "Lexical_profiles_3")      # Manually adjust the profiles that are evaluated 

    file_path = os.path.join(dir, str(timeframe)+"_database.json")
    with open(file_path, 'r', encoding = "utf-8") as f:
        database = json.load(f)

    ngrams = database["ngrams"]["common"]
  
    return database, ngrams 

## Create the results csv file for the Lexical Alignment evaluation
results_path = os.path.join("Results", "results_LA_summary_train_30_3.csv")     # Manually adjust the name for the evaluation that was done.
os.makedirs(os.path.dirname(results_path), exist_ok=True)
results_file = open(results_path, mode="w", newline="", encoding="utf-8")
writer = csv.writer(results_file)
writer.writerow([
    "Model", "Transcript_nr", "Timeframe_LP", "Timeframe_EVAL", "Split",
    "Amount", "Metric", "Value", "POS", "Matchtype"
])

def word_based_measures(tokens_O, tokens_GEN, pos, transcript, timeframe_LP, timeframe_EVAL, split):
    ## Exact repetition
    COS_E = compute_cosine_similarity(tokens_O, tokens_GEN)
    Recall_E, Coverage_E = compute_recall_coverage(tokens_O, tokens_GEN, list_of_words = True, generated_questions=False)

    # Store exact measures
    for metric, val in zip(
        ["Recall", "Coverage", "Cosine"],
        [Recall_E, Coverage_E, COS_E]
    ):
        writer.writerow([
            "Lexical profile", transcript, timeframe_LP, timeframe_EVAL, split,
            0, metric, val, pos, "Exact"
        ])
    ## Lemmatised repetition
    tokens_O = [lemmatize_cached(p) for p in tokens_O]
    tokens_GEN = [lemmatize_cached(p) for p in tokens_GEN]
    COS_L = compute_cosine_similarity(tokens_O, tokens_GEN)
    Recall_L, Coverage_L = compute_recall_coverage(tokens_O, tokens_GEN, list_of_words = True, generated_questions=False)

    # Store lemma measures
    for metric, val in zip(
        ["Recall", "Coverage", "Cosine"],
        [Recall_L, Coverage_L, COS_L]
    ):
        writer.writerow([
            "Lexical profile", transcript, timeframe_LP, timeframe_EVAL, split,
            0, metric, val, pos, "Lemma"
        ])

def ngram_based_measures(text_O, ngrams_GEN, transcript, timeframe_LP, timeframe_EVAL, split):
    n_values = [2,3,4,5]
    ngrams_O = []
    sentences = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', text_O)

    
    for n in n_values:
        all_ngrams = get_ngram(sentences, int(n))
        ngrams_O.extend(all_ngrams)
    # Exact repetition
    Recall_ngram_E, Coverage_ngram_E = compute_recall_coverage(ngrams_O, ngrams_GEN, list_of_words = True, generated_questions=False)

    # Store exact measures
    for metric, val in zip(
        ["Recall", "Coverage", "Cosine"],
        [Recall_ngram_E, Coverage_ngram_E, None]
    ):
        writer.writerow([
            "Lexical profile", transcript, timeframe_LP, timeframe_EVAL, split,
            0, metric, val, "ngram", "Exact"
        ])

    ## Lemmatised repetition
    ngrams_O = [lemmatize_cached(p) for p in ngrams_O]
    ngrams_GEN = [lemmatize_cached(p) for p in ngrams_GEN]
    Recall_ngram_L, Coverage_ngram_L = compute_recall_coverage(ngrams_O, ngrams_GEN, list_of_words = True, generated_questions=False)

    # Store lemma measures
    for metric, val in zip(
        ["Recall", "Coverage", "Cosine"],
        [Recall_ngram_L, Coverage_ngram_L, None]
    ):
        writer.writerow([
            "Lexical profile", transcript, timeframe_LP, timeframe_EVAL, split,
            0, metric, val, "ngram", "Lemma"
        ])

## Obtain the results
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
directory = os.path.join(parent_dir, "Data")
folders = [f for f in os.listdir(directory) if f.isdigit()]

timeframes = [5, 10, 15, 20, 25, 30]        # The timeframes at which a lexical profile was created
split_increase = 30      # The splits that are used to evaluate the lexical profile, this was at 10 and 30

## Loop over all the transcripts
for transcript in folders:
    print(transcript)
    file_path = os.path.join(directory, transcript)

    # Get the file of transcript splits for the current transcript
    dir = os.path.join(directory, transcript)
    file_p = os.path.join(dir, "splits" + '.json')
    with open(file_p, "r", encoding = "utf-8") as file:
            data = json.load(file)

    ## Loop over the timeframes at which the lexical profiles were generated
    for timeframe in timeframes:
        print(timeframe)
        t = timeframe
        split_start = timeframe

        while split_start + split_increase <= max(map(int, data.keys())):
            split_end = split_start + split_increase

            ### Get the data for the next timeframe block to be compared with
            text_O, tokens_O = preprocess(data, split_start, split_end)  
            POS_terms_O, _, _ = frequency_term_POS(tokens_O, 5, target_pos=["NOUN", "PRON", "ADJ", "CONJ", "VERB", "ADV"])                                     
                                                # This number does not need to change!

            ### Obtain the generated results for this transcript at this timeframe
            database, ngrams_GEN = get_generated(file_path, t)
            POS_list = ["NOUN", "PRON", "ADJ", "CONJ", "VERB", "ADV"]
            for i in POS_list:
                tokens_GEN = database[i]["common"]
                tokens_O = POS_terms_O[i]
                word_based_measures(tokens_O, tokens_GEN, i, transcript, t, f"{split_start} - {split_end}", split_increase)
            ngram_based_measures(text_O, ngrams_GEN, transcript, t, f"{split_start} - {split_end}", split_increase)
            
            split_start = split_end

lemmatize_cached.cache_clear()

