"""
In this script, the revised functions 'preprocess(file_path, timeframe)' and 'def preprocess(data, start, end, Full = False)' are presented.
"""

def preprocess(file_path, timeframe):
    """ This function is used within the 'get_lexical_features.py' """
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
        t4 = t3.replace("  ", " ")

        t5 = re.sub(r'-\s+(?=[A-Z0-9])', ' BREAK ', t4)
        t6 = re.sub(r'-\s+(?=[a-z0-9])', ' BREAK ', t5)
        t7 = re.sub(r'(\w+)-$', r'\1 BREAK ', t6.strip())
        text_ += t7
        doc = nlp(t7)

        tokens = [token.text.lower() for token in doc
                  if (token.is_alpha or token.text == ',')
                  and token.text not in {"PAUSE", "BREAK"}]
        tokens_.extend(tokens)
    return text_, tokens_


def preprocess(data, start, end, Full=False):
    """ This function is used within the 'function.py' """
    start_ = int(start / 5)
    end_ = int(end / 5)
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
        t7 = re.sub(r'(\w+)-$', r'\1 BREAK ', t6.strip())
        text_ += t7
        doc = nlp(t7)

        tokens = [token.text.lower() for token in doc
                  if (token.is_alpha or token.text == ',')
                  and token.text not in {"PAUSE", "BREAK"}]
        tokens_.extend(tokens)

    return text_, tokens_
