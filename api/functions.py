import math
import json
import scipy
import pickle
import numpy as np 
import pandas as pd

from operator import itemgetter
from tinydb import TinyDB, Query

"""
FUNCTIONS FOR THE API
-----------------------------------------------------

FILES REQUIRED:
    -- Similarity matrix for dataset titles
     - ../data/pairwise_similarity_titles.pkl 
    -- Similarity matrix for dataset descriptions
     - ../data/pairwise_similarity_descriptions.pkl
     
    -- Catalog (to be changed)
     - ../data/catalog.csv
     
    -- List of names of stored categorical columns
     - ../data/namesCategoric.pkl
    -- List of numeric columns with statistical descriptions
     - ../data/categorical_description.json

     
TO DO:
    -- Change catalog.csv to be read from database

"""

##########################
# INTERNAL
##########################

"""
internal function for catalog()
returns the list of columns from all the datasets that are 
similar to a specific dataset column
"""
def categoricalSimilarity(datasetId, columnName):
    SIZE = 5 # number of columns to return
    db = TinyDB("../data/catalog.json")

    # open similarity matrix for categorical rows
    with open("../data/similarityMatrixCategoric.pkl", "rb") as fp:  
        similarityMatrix = pickle.load(fp)
    with open('../data/categorical_description.json', 'r') as f:
        categorical_description = json.load(f)

    # identify column index inside namesCategoric
    columnIndex = -1
    for i in range(len(categorical_description)):
        element = categorical_description[i]
        if element['datasetIndex'] == datasetId and element['columnName'] == columnName:
            columnIndex = i
        if element['datasetIndex'] > datasetId: break

    # return empty if not found
    if(columnIndex == -1):
        return []
    else: 
        similarityVector = similarityMatrix[columnIndex].toarray().tolist()[0]
        similarity_vector_sorted = sorted(similarityVector, reverse=True)

        similarityIndex = []
        for i in range(len(similarityVector)):
            similarityIndex.append([i, similarityVector[i]])

        sortedIndex = sorted(similarityIndex, key=itemgetter(1), reverse=True)

    result = []
    for element in sortedIndex[0:5]:
        columnDescription = categorical_description[element[0]]
        datasetId = columnDescription['datasetIndex']
        columnName = columnDescription['columnName']
        value = round(element[1], 2)
        result.append({
            'datasetId': datasetId,
            'datasetTitle': db.search(Query().index == int(datasetId))[0]['title'],
            'datasetUrl': db.search(Query().index == int(datasetId))[0]['web_url'], 
            'name': columnName, 
            'value': value
        })
        
    return(result)

# cosine similarity between two vectors of same length
def cosine_similarity(a,b):
    cos_sim = np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))
    return cos_sim

"""
# Numeric
# remove rows with nan or malformed results from the output
# fast, around 120000 rows
"""
def returnCleanOutput(numerical_description):
    cleanOutput = []
    for element in numerical_description:
        if(len(element['description']) == 8):
            noNan = True
            for value in element['description']:
                if(math.isnan(value)): noNan = False
            if(noNan):
                cleanOutput.append(element)
        else: pass    # bad formatting
    return cleanOutput



"""
internal function for catalog()
calculate similarity between a spceific numerical row and everything else
"""    
def columnSimilarities(columnIndex, cleanOutputNum):
    # Don't keep values below thershold to have a faster sorting
    THRESHOLD = 0.9 
    SIZE = 5
    
    column = cleanOutputNum[columnIndex]
    datasetIndex = column['datasetIndex']
    
    result = []
    for i in range(0, len(cleanOutputNum)):
        dataset_i = cleanOutputNum[i]['datasetIndex']
        if(dataset_i != datasetIndex):
            cs = cosine_similarity(cleanOutputNum[columnIndex]['description'], cleanOutputNum[i]['description'])
            if(cs > THRESHOLD):
                result.append(
                [
                    {
                        'datasetId':  cleanOutputNum[i]['datasetIndex'],
                        'name': cleanOutputNum[i]['columnName']
                    }, 
                    cs
                ])
    
    sortedResult = (sorted(result, key=itemgetter(1), reverse=True))[0:SIZE]
    jsonResult = []
    for element in sortedResult:
        element[0]['value'] = round(float(element[1]), 2)
        jsonResult.append(element[0])
    return jsonResult
    

"""
internal function for catalog()
returns the list of columns from all the datasets that are 
similar to a specific dataset column
"""
def numericalSimilarity(datasetId, columnName):

    SIZE = 5

    with open("../data/numerical_description.json") as fp:  
        numerical_description = json.load(fp)

    # remove malformed columns with nans
    cleanOutputNum = returnCleanOutput(numerical_description)

    # identify column index inside namesCategoric
    columnIndex = -1
    for i in range(len(cleanOutputNum)):
        element = cleanOutputNum[i]
        if element['datasetIndex'] == datasetId and element['columnName'] == columnName:
            columnIndex = i
        if element['datasetIndex'] > datasetId: break

    # return empty if not found
    if(columnIndex == -1):
        #return []
        print([])

    return columnSimilarities(columnIndex, cleanOutputNum)


# List of datasets recomended from column profile similarities
def profileRecomendations(itemId, columns):
    
    SIZE = 4                  # number of datasets to return
    similarities = dict()     # keep track of cummulative dictionaries for each dataset

    for column in columns:
        for similarColumn in column["similar"]:
            # Only keep values larger that 0.9/100 
            # to avoid considering columns with low similarity
            if similarColumn['value'] > 0.9:
                
                columnObj = {
                    "originalColumn": column["name"],
                    "similarColumn": similarColumn['name'],
                    "value": similarColumn['value']
                }
                
                if similarColumn['datasetId'] in similarities: 
                    similarities[similarColumn['datasetId']].append(columnObj)
                else: 
                    similarities[similarColumn['datasetId']] = [columnObj]

    result = []                
    for key in list(similarities.keys()):
        
        datasetSimilarity = 0
        similarColumnslist = []
        for columnValue in similarities[key]:  
            datasetSimilarity += float(columnValue["value"])
            similarColumnslist.append([{
                "originalColumn": columnValue["originalColumn"], 
                "similarColumn": columnValue["similarColumn"]
            }])
            
        # Get information about dataset for the frontend
        db = TinyDB("../data/catalog.json")
        datasetObj = db.search(Query().index == int(key))[0]

        result.append({
            "datasetId": key,
            "datasetInformation": {
                "title": datasetObj["title"],
                "description": datasetObj["description"],
                "origin": datasetObj["origin"]
            },
            "datasetSimilarity": datasetSimilarity,
            "countSimilarColumns": len(similarities[key]),
            "similarColumns": similarColumnslist
        })

    # sort by number of similar columns
    result.sort(key=lambda x: x["countSimilarColumns"], reverse=True)

    # keep only good values
    result = result[:SIZE]

    return(result)



    
"""
internal function for catalog()
returns the list of all columns in the dataset if possible
    otherwise returns empty
    
Categorical columns are defined in a list of names, because the similarity 
is derived from a numpy matrix of similarities (tfidf)

Numerical columns come with the statistical description of pandas.describe
[count, mean, std, min, 25%, 50%, 75%, max]  

Also retrieves a list of 5 columns from other datasets that are similar
(cosine similarity over pd.describe for nuimerical and tfidf for categorical)
"""
def getcolumnNames(datasetId):
    datasetId = str(datasetId)

    # list of numerical columns with statistical description
    with open("../data/numerical_description.json") as fp:  
        numerical_description = json.load(fp)
        
    with open('../data/categorical_description.json', 'r') as f:
        categorical_description = json.load(f)

    columns = []

    # Categorical columns
    for element in categorical_description:
        if element['datasetIndex'] == datasetId:
            columns.append(
            {
                'type': ' categorical', 
                'name': element['columnName'], 
                'similar': categoricalSimilarity(datasetId, element['columnName'])
            })
        if element['datasetIndex'] > datasetId: break
            
            
    # Numerical columns
    for element in numerical_description:
        if element['datasetIndex'] == datasetId:
            columns.append(
            {
                'type': ' numerical', 
                'name': element['columnName'], 
                'similar': numericalSimilarity(datasetId, element['columnName'])
            })
        if element['datasetIndex'] > datasetId: break
    
    return columns

"""
Returns list of datasets ids ordered by similarity 
based on title and description texts (TF-IDF similarity)
"""
def descriptionSimilarity(itemId):
    # coef: percentage of importance given to description similarity vs title similarity
    #       coef * desc_sim + (1 - coef) * title_sim
    COEF = 0.7

    itemId = int(itemId)
    
    # Retrieve similaity matrices
    with open("../data/pairwise_similarity_titles.pkl", "rb") as input_file:
        pairwise_similarity_title = pickle.load(input_file)
        pairwise_similarity_title = np.array(pairwise_similarity_title)
    with open("../data/pairwise_similarity_descriptions.pkl", "rb") as input_file:
        pairwise_similarity_desc = pickle.load(input_file)
        pairwise_similarity_desc = np.array(pairwise_similarity_desc)
    
    # Calculate similarity
    pairwise_similarity = np.add(COEF * pairwise_similarity_title, (1 - COEF) * pairwise_similarity_desc)
    pairwise_similarity = pairwise_similarity / 2

    # Change format and sort
    similarity_vector = pairwise_similarity[itemId] #.toarray()
    similarity_vector = list(similarity_vector)
    similarity_vector_sorted = sorted(similarity_vector, reverse=True)
    sorted_ind = [similarity_vector.index(i) for i in similarity_vector_sorted]

    return sorted_ind

# List of recomended dataset with information based on description similarity  
def recomendationsText(datasetIndex):
    descriptionSimilars = descriptionSimilarity(datasetIndex)[0:6]
    db = TinyDB("../data/catalog.json")
    result = []
    for indexVal in descriptionSimilars:
        if(indexVal != datasetIndex):
            itemObj = db.search(Query().index == int(indexVal))[0]
            result.append(itemObj)
    return(result)


##########################
# API ENDPOINTS
##########################


"""
API ENDPOINT
url => ... /catalog
Retrieve all information from the catalog csv in json format

{'index': 0, 
'title': 'Unitats administratives  de la ciutat de Barcelona', 
'description': 'Detall de les unitats administratives  de la ciutat de Barcelona:  districtes, barris, àrea interès, àrees estadístiques bàsiques (AEB) i seccions censals  ', 
'category': 'Administració', 
'date_published': '2017-07-06', 
'source': 'Ajuntament de Barcelona', 
'web_url': 'https://opendata-ajuntament.barcelona.cat/data/ca/dataset?q=&name=20170706-districtes-barris', 
'download_url': 'https://opendata-ajuntament.barcelona.cat/data/dataset/808daafa-d9ce-48c0-925a-fa5afdb1ed41/resource/4cc59b76-a977-40ac-8748-61217c8ff367/download', 
'status': '-', 
'origin': 'Barcelona'}

"""
def catalog():
    # Instead od db.all() an iteration for all the elements has to 
    # be made because fastAPI is stupid and cant handle nans
    # will be solved at the database craetion
    result = []
    db = TinyDB("../data/catalog.json")
    for element in db:

        for column in element:
            if str(element[column]) == 'nan':
                element[column] = str(element[column])
        # if str(element['organization_name']) == 'nan':
        #    element['organization_name'] = str(element['organization_name'])
        result.append(element)
    return result
    

"""
API ENDPOINT
URL => ... /item/{itemId}
Retrieve information from a single object (dataset)
"""
def retrieveItem(itemId):
    db = TinyDB("../data/catalog.json")
    itemObj = db.search(Query().index == int(itemId))[0]
    itemObj['columns'] = getcolumnNames(itemId)
    itemObj['recomendations'] = recomendationsText(itemId)
    itemObj['profileRecomendations'] = profileRecomendations(itemId, itemObj['columns'])

    return itemObj


##########################
# FRONTEND INFORMATION
##########################

def MainPage():
    with open('frontend/MainPage.json') as json_file:
        data = json.load(json_file)
        return(data)

def Catalog():
    with open('frontend/Catalog.json') as json_file:
        data = json.load(json_file)
        return(data)

def DataSource(source):
    with open('frontend/DataSources.json') as json_file:
        data = json.load(json_file)
        try:
            return data[source]
        except:
            return []
        
