import spacy
from collections import Counter
import re
import json
import os

"""
This script was used to extract the lexical profiles per transcript
"""

# Load Dutch spaCy model used for POS tagging and tokenization
nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  # Or however large the input is


def preprocess(file_path, timeframe):
    """
    This function takes two arguments, one for the file and one for the amount of timeframes, 
    and returns the corresponding text and tokens.
    
    Parameters:
    arg1 (file_path): the filepath to the interview
    arg2 (timeframe: the integerer corresponding to the nr of timeframes used in the simulation
    
    Returns:
    string: the cleaned text, list: the tokens from the text
    """
    with open(file_path, "r", encoding = "utf-8") as file:
          data = json.load(file)
    
    # Get the first integer items from the dictionary list
    integer = int(timeframe/5 )
    texts = list(data.values())[:integer]

    text_ = ""
    tokens_ = []

    for text in texts:    
        t1 = text.replace("\n", "")          
        t2 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', t1)
        t3 = re.sub(r'…(?=\W)', ' PAUSE', t2)
        t4 = t3.replace("  ", " ") #.replace(" .", ".")
                
        t5 = re.sub(r'-\s+(?=[A-Z0-9])', ' BREAK ', t4) 
        t6 = re.sub(r'-\s+(?=[a-z0-9])', ' BREAK ', t5)    
        text_ += t6
        text_ = re.sub(r'(\w+)-$', r'\1 BREAK ', text_.strip())


        doc = nlp(text_)
        tokens = [token.text.lower() for token in doc 
                  if (token.is_alpha or token.text == ',') 
                  and token.text not in {"PAUSE", "BREAK"}]
        tokens_.extend(tokens)

        
    return text_, tokens_

def get_token_POS(doc):
    """
    This function takes one argument and returns the POS category per item
    
    Parameters:
    arg1 (doc): the tokens of which we want to obtain the POS label
    
    Returns:
    list: A list of POS values for the input tokens
    """
    pos = []
    for token in doc:
        if token.text in {".", "!", "?"}: 
            continue
        elif token.text == "PAUSE":
            pos.append("PAUSE")
        elif token.text == "BREAK":
            pos.append("BREAK")
        elif token.pos_ in {"NOUN", "PROPN"}:
            pos.append("NOUN")
        elif token.pos_ in {"CONJ", "SCONJ", "CCONJ"}:
            pos.append("CONJ")
        elif token.pos_ in {"VERB", "AUX"}:
            pos.append("VERB")
        elif token.pos_ == "INTJ" or token.text.lower() == "eh" or token.text.lower() == "ehm":            
            pos.append("INTJ")
        else:
            pos.append(token.pos_)
    
    return pos

def sentence_POS(text):
    """
    This function takes one argument and returns its dictionary with the sentence and its corresponding POS structure
    
    Parameters:
    arg1 (text): the text
    
    Returns:
    dictionary: sentence and their corresponding POS structure
    """
    sentences = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', text)
    pos_dict = {}
    for s in sentences:
        if s == "":
            continue
        doc = nlp(s)
        pos = get_token_POS(doc)
        s = s.strip(".!?")
        pos_dict[s] = pos
    return pos_dict

def get_sentence_length(sentences):
    """
    This function takes one argument and returns the avg sentence length and the std
    
    Parameters:
    arg1 (sentences): the sentences
    
    Returns:
    float: avg sentence length, Any: std
    """
    s_length = []  
    for s in sentences:
        doc = nlp(s)
        count = sum(1 for token in doc if not token.is_punct and token.text != "PAUSE" and token.text != "BREAK")
        s_length.append(count)
    mean = sum(s_length) / len(s_length)
    return mean


def get_ngram(data, n, x):
    """
    This function returns the amount of identical ngrams in the provided data (sentences) where n is specified as argument    
    Parameters:
    arg1 (data): the data, sentences
    arg2 (n): the n for ngrams
    arg3 (x): the parameter indicating how many of the top common we want to return
    
    Returns:
    list[tuple(pattern, int)]
    """
    patterns = []
    for d in data: 
        doc = nlp(d) 
        tokens = []
        for i, token in enumerate(doc):
            if (token.text == ',' or token.text == '.') and i > 0:
                tokens[-1] = tokens[-1] + token.text
            else:
                tokens.append(token.text)
        # tokens = [token.text for token in doc]  
        ngrams = zip(*[tokens[i:] for i in range(n)])  
        patterns.extend([' '.join(ngram) for ngram in ngrams])

    pattern_counter = Counter(patterns)  
    all_patterns = [pattern for pattern in pattern_counter]
    threshold = 3   # Threshold measure
    top_patterns = [pattern for pattern, count in pattern_counter.most_common(x) if count > threshold]  
    return top_patterns, all_patterns


def frequency_term_POS(tokens, x, target_pos = None):
    """
    This function returns the terms per POS category, 
    the frequency of the categories (based on the amount of terms present), 
    and the most common x (param) terms per category
    
    Parameters:
    arg1 (tokens): the tokens of which we want to know this information
    arg2 (x): the variable indicating how much values we want to return
    arg3 (target_pos): List of POS categories to include in the result

    Returns:
    dictionary: with the POS category and corresponding tokens
    list[tuple(pos category, count)]: the pos categories and their counts (ordered descending)
    dict[pos category, x most common terms]
    """
    pos_dict = {}
    doc = nlp(" ".join(tokens))  
    pos_ = get_token_POS(list(doc))  

    for i, t in enumerate(tokens):
        tag = pos_[i]
        if tag in {"PAUSE", "BREAK"}:
            continue
        if target_pos and tag not in target_pos:
            continue
        pos_dict.setdefault(tag, []).append(t)
    total_counts = {pos: len(terms) for pos, terms in pos_dict.items()}
    sorted_counts = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)
    threshold = 5   # threshold measure 
    common_terms = {
        pos: [term for term, count in Counter(terms).most_common(x) if count > threshold]
        for pos, terms in pos_dict.items()
}    
    return pos_dict, sorted_counts, common_terms


### Here, the database for the features used in lexical alignment will be created. 
### The top x amount of ngrams / words are stored in a separate part of this database.
### Loop through all the interview transcriptions

# A set list of timeframes is chosen for which the lexical profiles are obtained. Adjust where necessary
timeframes = [5,10,15,20,25,30]     ## Training data
# timeframes = [10]                   ## Holdout data

directory = "Data"
for transcript in os.listdir(directory):
    # transcript = "1413"
    print(f"Processing: {transcript}")
    ID = transcript.strip()  
    database = {}
    database["ID"] = {
        "transcript number": ID
    }

    # Get the file of transcripts splits for this ID
    dir = os.path.join("Data", ID)      # Switch to holdout folder if necessary
    file_path = os.path.join(dir, "splits" + '.json')

    for timeframe in timeframes:
        print(f"Timeframe: {timeframe}")
        # Preprocess the transcribed data, note that the integer here represents the used timeframes
        text, tokens = preprocess(file_path, timeframe)    

        # Here, the lexical features are extracted and stored in the database. 
        # Note that there is a frequency threshold specified within the function itself. 
        pos_structure = sentence_POS(text)
        sentences = list(pos_structure.keys())  # Text per sentences
        POS = list(pos_structure.values())      # POS categories per sentence
                                                    
        # These target_pos is determined by the affected properties in dementia speech
        # The integer represents the nr of terms included per POS category

        ## This line was used for the training data
        POS_terms, _, POS_common = frequency_term_POS(tokens, 20, target_pos=["NOUN", "PRON", "CONJ", "ADJ", "VERB", "ADV"]) 
        
        ## These lines were used for the holdout data
        # POS_terms_1, _, POS_common_1 = frequency_term_POS(tokens,5, target_pos=["CONJ", "ADJ"])  
        # POS_terms_2, _, POS_common_2 = frequency_term_POS(tokens, 10, target_pos=["PRON","NOUN", "VERB", "ADV"])   
        # POS_terms = {**POS_terms_1, **POS_terms_2}
        # POS_common = {**POS_common_1, **POS_common_2}                                                                     
        
        for pos in POS_terms:
            database[pos] = {
                "terms": list(set(POS_terms[pos])),  # only save each term once
                "common": POS_common.get(pos, [])
            }


        # Here, the ngrams are retrieved, and stored in the database 
        # Note that there is a frequency threshold specified within the function itself.
        n_values = [2,3,4,5]
        ngrams_common = []
        ngrams_all = []
        for n in n_values:
            ngrams, all_ngrams = get_ngram(sentences, int(n), 3)    # The integer represent the amount of ngrams to be returned
            ngrams_common.extend(ngrams)
            ngrams_all.extend(all_ngrams)
        database["ngrams"] = {
            "ngrams_all": ngrams_all,
            "common": ngrams_common
        }

        # Get the interview excerpt
        file_path_ov = os.path.join(dir, "transcript_overview.json")

        # Finally the database is created as a JSON file
        q = os.path.join(dir, "Lexical_profiles")
        os.makedirs(q, exist_ok=True) 
        p = os.path.join(q, str(timeframe) + "_database" + '.json')
        with open(p, "w", encoding="utf-8") as f:
            json.dump(database, f, ensure_ascii=False, indent=4)
