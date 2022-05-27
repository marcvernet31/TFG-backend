import pickle
import numpy as np
import pandas as pd

from tinydb import TinyDB
from stopwords_ca import batch
from sklearn.feature_extraction.text import TfidfVectorizer


"""
Similarity between arrays of texts based on TF-IDF
Creates a matrix of similarities for titles and for descriptions

Execute:
    $> conda run -n similarity-new python3 text-similarity/similarityMatrices.py

Generates:
    -- data/pairwise_similarity_titles.pkl => TF-IDF similarity for titles
    -- data/pairwise_similarity_descriptions.pkl => TF-IDF similarity for descriptions 
"""


# Punctiation chars to be removed
punctuations = "!#$%&'()*+,-./:;?@[\]^_`{|}~"
# Added words to stopwords
batch += ["l", "d", "\\n"]


# Clean a text for NLP
# remove stopwords, punctuation, ...
def preprocess(text):

    if type(text) == float: text = "-"     # remove possible nan
    text = text.strip()                    # remove \n
    for p in punctuations:                 # remove puntuations
        try: text = text.replace(p, ' ')
        except: print(text)
        
     
    text = text.lower()                    # remove capital letters        
    text = ' '.join(                       # remove stopwords
        [x for x in text.split(' ') if x not in batch]
    )
    
    return text


# Preprocess a list of texts
def preprocess_text_list(text_list):
    return [(lambda x: preprocess(x))(x) for x in text_list]


# Genereate pairwaise similarity matrix from an array of texts
def gen_pairwise_similarity(text):
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(text)  

    pairwise_similarity = tfidf * tfidf.T 
    return(pairwise_similarity)


def main():
    
    #catalog = pd.read_csv("../data/catalog.csv")
    catalog = TinyDB('data/catalog.json')

    print("Calculating title similarity matrix")

    # generate similarity matrix for titles
    titles = [r['title'] for r in catalog.all()]
    titles_clean = preprocess_text_list(titles)
    pairwise_similarity_titles = gen_pairwise_similarity(titles_clean)
    pairwise_similarity_titles_list = pairwise_similarity_titles.toarray().tolist()

    with open('data/pairwise_similarity_titles.pkl', 'wb') as f:
        pickle.dump(pairwise_similarity_titles_list, f)

    print("Calculating description similarity matrix")
    
    # generate similarity matrix for description
    #descriptions = list(catalog["description"])
    descriptions = [r['description'] for r in catalog.all()]
    descriptions_clean = preprocess_text_list(descriptions)
    pairwise_similarity_descriptions = gen_pairwise_similarity(descriptions_clean)
    pairwise_similarity_descriptions_list = pairwise_similarity_descriptions.toarray().tolist()

    with open('data/pairwise_similarity_descriptions.pkl', 'wb') as f:
        pickle.dump(pairwise_similarity_descriptions_list, f)


if __name__ == "__main__":
    main()