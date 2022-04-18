import io
import json 
import time
import pickle
import eventlet
import requests
import pandas as pd
from tinydb import TinyDB
from stopwords_ca import batch


"""
Extract the describe() profile for numerical columns and the full rows (clean) for categorical values
Generate: output_numeric.pkl, output_categoric.pkl


For some reason all the code does't work properly if its inside a main() function


ERRORS:
-- fa falta un token d'access
https://opendata-ajuntament.barcelona.cat/data/ca/dataset?q=&name=actes-anella 


-- requereixen un token (barcelona)

-- hospitalet "datasets" que no son csv

-- casos particulars
    -- 20: dataset buid
    -- 21: retorna un json
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


def categoricPreprocess(column):

    var_list = list(set(column))
    cleanValues = preprocess_text_list(var_list)

    words = []
    for element in cleanValues: words += element.split(' ')
    uniqueWords = list(set(words))

    return(uniqueWords)


def rowDescriptionTest(content, datasetIndex, numerical_description, categorical_description):
    LIMIT = 50
    data = io.StringIO(content)
    df = pd.read_csv(data, sep=',')
    types = df.dtypes
    description = df.describe()
    columns = list(df.columns)
        
    if(len(columns) < LIMIT): # avoid incorreclty formated rows (json wrongly identified as csv)
        for column_name in columns:

            # column is numerical
            if(column_name in list(description.columns) 
                and (types[column_name] == 'int64' or types[column_name] == 'float64')
            ):
                desc = {
                        'datasetIndex': str(datasetIndex), 
                        'columnName': column_name, 
                        'description': list(description[column_name])
                }
                numerical_description.append(desc)
                print(f"-- {column_name}: NUMERICAL")
                print(' - description: ', desc['description'])

            # column is categorical
            else:
                if(len(column_name) < 20): # avoid malformated columns (long colums names)
                    desc = {
                        'datasetIndex': str(datasetIndex), 
                        'columnName': column_name, 
                        'description': categoricPreprocess(df[column_name])
                    }

                    categorical_description.append(desc)
                    print(f"-- {column_name}: CATEGORICAL")
                    print(' - world lenght: ', len(desc['description']))



        print("Success loading dataset")
    else:
        print("Error in format, avoiding load")




###### MAIN ##############################
def main():
    TIMEOUT_SECONDS = 10
    numerical_description = []
    categorical_description = []
    errors = []

    correctlyReadCounter = 0
    totalCounter = 0

    db = TinyDB('data/catalog.json')
    #db = TinyDB('../data/catalog.json')

    for dataset in db.all():
        print("Index: ", dataset['index'])
        url = dataset["download_url"]
        print(url)

        # extract content from url   
        try:
            with eventlet.Timeout(TIMEOUT_SECONDS):
                req = requests.get(url)
        except:
            print("ERROR: timeout, too slow")
            errors.append({"index": dataset['index'], "error":'timeout'})

        # process
        try:
            # Identified as utf-8
            content = req.content.decode("utf-8")
            # Check if its json
            if((content[0] == '[' and content[len(content)-1] == ']')
                or content[0] == '{' and content[len(content)-1] == '}'
            ):
                print("Format identified: json")
                # Decode json and convert to csv
                # ....
            else:   
                print("Format identified: csv utf-8")
                rowDescriptionTest(content, dataset["index"], numerical_description, categorical_description)
                correctlyReadCounter += 1
        except: 
            # content cant be downloaded in utf-8, try utf-16
            print('Format not identified')
            pass
        totalCounter += 1
        print('-------------------')

    with open('data/numerical_description.json', 'w') as f:
        json.dump(numerical_description, f)
    with open('data/categorical_description.json', 'w') as f:
        json.dump(categorical_description, f)

    print('-----------------')
    print("Total number of datasets: ", totalCounter)
    print("Correctly read: ", correctlyReadCounter)

if __name__ == '__main__':
    main()