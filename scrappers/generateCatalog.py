import subprocess
import pandas as pd

from tinydb import TinyDB
from scrapperBarcelona import Barcelona_df
from scrapperHospitalet import Hospitalet_df

"""
Unify all scrapped sources into a single dataset

To do:
    - All datasets should provide the same columns
"""

def main():

    try:
        subprocess.run(["mkdir", "data"])
        print("-- Directory ./data created")
    except:
        print("-- Directory ./data already exists")

    
    # Barcelona
    try:
        catalogBarcelona = Barcelona_df()           
    except Exception as err:
        print("ERROR: error scrapping OpenData Barcelona at scrapperBarcelona.py")
        raise(err)

    # Hospitalet
    try:
        catalogHospitalet =  Hospitalet_df() 
    except Exception as err:
        print("ERROR: error scrapping Hospitalet data at scrapperHospitalet.py")
        raise(err)      

    
    catalog = catalogBarcelona.append(catalogHospitalet, ignore_index=True)
    catalog["index"] = list(range(0, len(catalog)))
    
    #catalog.to_csv("data/catalog.csv", index=False)

    print("--- Generating DB ---")

    # catalog.json is the TinyDB that will be used in the project
    db = TinyDB('data/catalog.json')

    # Format rows into json and insert to db
    for index, row in catalog.iterrows():
            
        json_row = {
            'index': row['index'],
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'date_published': row['date_published'],
            'source': row['source'],
            'web_url': row['web_url'],
            'download_url': row['download_url'],
            'status': row['status'],
            'origin': row['origin']
        }
        
        db.insert(json_row)


if __name__ == "__main__":
    main()