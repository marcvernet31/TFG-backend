import time
import math
import json
import pickle
import numpy as np
import pandas as pd

from stopwords_ca import batch
from operator import itemgetter
from sklearn.feature_extraction.text import TfidfVectorizer

"""
Generate d¡the TFIDF similarity matrix for categorical rows

conda run -n similarity-new python3 atribute-similarity/similarityCategoricMatrix.py
 
"""

#### PREPROCESS

# Genereate pairwaise similarity matrix from an array of texts
def gen_pairwise_similarity(text):
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(text)  

    pairwise_similarity = tfidf * tfidf.T 
    return(pairwise_similarity)

def generateSimilarityMatrix():

    with open('data/categorical_description.json', 'r') as f:
        categorical_description = json.load(f)

    columnNames = []
    texts = []
    for column in categorical_description:
        columnName = column['columnName']
        values = column['description']
        joinValues = ' '.join(values)
        
        texts.append(joinValues)
        columnNames.append(columnName)

    similarityMatrix = gen_pairwise_similarity(texts)
    
    with open("data/similarityMatrixCategoric.pkl", "wb") as fp:  
        pickle.dump(similarityMatrix, fp)
        
    with open("data/namesCategoric.pkl", "wb") as fp:  
        pickle.dump(columnNames, fp)


def main():
    generateSimilarityMatrix()

if __name__ == '__main__':
    main()