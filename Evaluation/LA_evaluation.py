from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import string
from functools import lru_cache

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])

"""
This script was used to to obtain the recall, coverage, and cosine similarity scores
"""

@lru_cache(maxsize=None)
def lemmatize_cached(word: str) -> str:
    return lemmatize(word)


def lemmatize(n):
    doc = nlp(n.lower())
    return " ".join([token.lemma_ for token in doc])

# Function to calculate the precision, recall and F1 score
def compute_recall_coverage(overall_language, generated, list_of_words = False, generated_questions = True, verbose = False):
    # list_of_words = False means that there is inputted a sentence or generated question -> LLM responses
    # list_of_words = True means that there is inputted a list of generated words -> ngrams and words

    if list_of_words:
        gen = generated
    else:
        gen = generated[0].split()
        if generated_questions:
            gen = [word.strip(string.punctuation).lower() for word in gen]
        
    generated = set(generated)
    gen_set = set(gen)
    overlap = set()

    for v in overall_language:
        if v in gen_set:
            overlap.add(v)

    recall = len(overlap) / len(gen_set) if gen else 0
    coverage = len(overlap) / len(set(overall_language)) if overall_language else 0

    if verbose:
        print("Vocabular:", overall_language)
        print("Generated:", generated)
        print("Gen", gen)
        print("length:", len(gen_set))
        print("Set:", overlap)
    return recall, coverage

# Function to calculate the cosine similarity between two word lists
def compute_cosine_similarity(overall_language, generated, verbose=False):
    overall_language_ = " ".join(overall_language)
    generated_ = " ".join(generated)

    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform([overall_language_, generated_]).toarray()

    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0, 0]

    if verbose:
        print("Vocabular:", overall_language_)
        print("Generated:", generated_)
        print("Vocabulary space:", vectorizer.get_feature_names_out())
        print("Vocabulary_vec:", vectors[0])
        print("Generated_vec:", vectors[1])
        print("Cosine Similarity:", similarity)

    return similarity

