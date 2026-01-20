from collections import Counter
import re
import spacy

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  # Or however large the input is

""" 
Here various functions from the get_lexical_features file are stored (slightly adjusted if necessary) to be reused in different scripts 
"""

""" Preprocess the data to get a list of all the words from the interviewee """
def preprocess(data, start, end, Full = False):
    start_ = int(start/5)    
    end_ = int(end/5)
    texts = list(data.values())[start_:end_]
    if Full:
        texts = list(data.values())
    text_ = ""
    tokens_ = []

    for text in texts:    
        t1 = text.replace("\n", "")          
        t2 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', t1)
        t3 = re.sub(r'…(?=\W)', ' PAUSE', t2)
        t4 = t3.replace("  ", " ")
                
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

""" Function to obtain sentence length and the counts per sentence length """
def get_sentence_length(sentences):
    s_length = []
    for s in sentences:
        doc = nlp(s)
        count = sum(1 for token in doc if not token.is_punct and token.text not in ["PAUSE", "BREAK"])
        if count == 0:
            continue
        s_length.append(count)

    mean = sum(s_length) / len(s_length) if s_length else 0
    length_counts = Counter(s_length)

    return mean, length_counts

""" Obtain the ngrams """
def get_ngram(data, n):
    patterns = []
    for d in data: 
        doc = nlp(d) 
        tokens = []
        for i, token in enumerate(doc):
            if token.text == ',' and i > 0:
                # Concatenate the comma with the previous token
                tokens[-1] = tokens[-1] + token.text
            else:
                tokens.append(token.text)
        ngrams = zip(*[tokens[i:] for i in range(n)])  
        patterns.extend([' '.join(ngram) for ngram in ngrams])

    pattern_counter = Counter(patterns)  
    all_patterns = [pattern for pattern in pattern_counter]
    return all_patterns

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
    threshold = 5   # threshold measure for frequency of repetition
    common_terms = {
        pos: [term for term, count in Counter(terms).most_common(x) if count > threshold]
        for pos, terms in pos_dict.items()
}    
    return pos_dict, sorted_counts, common_terms
