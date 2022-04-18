import json
import requests
import pandas as pd

"""
Scrapper for OpenData Barcelona website
    https://opendata-ajuntament.barcelona.cat/

Retrieves all available datasets with title, description, page url, download url ...
Most part of the data is retrieved from the catalog csv file provided from the website
The links to download the files are extracted from the API endpoint "current_package_list_with_resources"

title 	
description 	
category 	
date_published 	
source 	
web_url 	
download_url 	
status 	
origin

"""

ORIGIN = "Barcelona"

# Retrieve urls to download files
def barcelona_url_retrieve(checkStatus):

    print("--- Scrapping OpenData Barcelona ---")

    # Retrieve list of all datasets available
    x = requests.get('https://opendata-ajuntament.barcelona.cat/data/api/3/action/current_package_list_with_resources?limit=2000')
    resources = json.loads(x.text)

    print(" - Catalog downloaded")
    print(" - Rerieving dataset information ...")

    data = []
    for dataset in resources["result"]:
    
        title = dataset['title_translated']['ca']
        web_url = dataset['url_tornada']['ca']
        download_url = dataset['resources'][0]['url']

        # OPTIONAL: check if the url works by making a request
        # status = csv => implies the link works and csv can be downloaded
        # if status is different csv can't be downloaded
        # With this amount of datasets it's TOO SLOW
        # For now all datasets seem to work
        status = "-"
        if(checkStatus):
            x = requests.get(download_url)
            status = x.status_code
        
        # data.append([title, web_url, download_url, '-', 'barcelona'])
        data.append([title, download_url, status, ORIGIN])

    return data


def Barcelona_df():
    # Download catalog provided by OpenData
    catalog_barcelona_url = "https://opendata-ajuntament.barcelona.cat/data/dataset/32d29a1f-f1bf-4250-a251-7638f1e8f4f1/resource/35f4fffd-95ae-40b6-8ef6-ca319ab666e4/download"
    catalog = pd.read_csv(catalog_barcelona_url)

    # Select and rename important columns
    catalog = catalog[["title_ca", "notes_ca", "organization_parent_name_ca", "date_published", "fuente", "url_busqueda_ca"]]
    catalog = catalog.rename(columns=
        {"title_ca":"title", "notes_ca":"description", "url_busqueda_ca":"web_url", "organization_parent_name_ca":"category", "fuente":"source"}
    )

    # Retrieve downloable links
    checkStatus = False
    data = barcelona_url_retrieve(checkStatus)
    #df_downloadUrl = pd.DataFrame(data, columns=['title', 'url', 'download_url', 'status', 'origin'])
    df_downloadUrl = pd.DataFrame(data, columns=['title', 'download_url', 'status', 'origin'])

    # Merge data 
    catalog = pd.merge(catalog, df_downloadUrl, on='title', how='inner')
    #catalog.to_csv("../data/catalog_Barcelona.csv")
    return catalog

