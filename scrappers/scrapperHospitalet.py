import time
import json
import requests

import pandas as pd 
from bs4 import BeautifulSoup


"""
Scrapper for the Hospitalet open data webiste:
    https://opendata.l-h.cat/

Retrieves all available datasets with title, description, page url, download url ...
There's an API, but it's only possible to retrieve data for individual datasets.
It retrieves around 100 datasets

To Do:
    - Also retrieve creation time and other data
"""

ORIGIN = "L'Hospitalet"
SOURCE = "Ajuntament de l'Hospitalet"

def Hospitalet_df():


    baseUrl = "https://opendata.l-h.cat/"                    # Base url for web scrapping
    baseURL_download = "https://opendata.l-h.cat/resource/"  # Base url to generate csv download url
    numberPages = 11                                         # Number of pages of datasets
    checkStatus = True                                       # Check if API dowenload link works (slow)

    print("--- Scrapping Hospitalet data ---")
    print(" -Rerieving dataset information ...")

    # Datasets are shown in pages that load approx, 10 dataset information
    # Iteration trhough all pages to extract all datasets
    retrievedData = []
    for i in range(1, numberPages):

        # Extract html for page
        url = baseUrl + f"browse?&page={i}"
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract html for individual dataset
        for dataset_soup in soup.find_all("div", class_="browse2-result"):
            title_soup = dataset_soup.find_all("h2")[0]
            title = title_soup.get_text().strip()
            link = title_soup.find_all("a")[0].get("href")

            # check if dataset provides description
            try:
                description = dataset_soup.find_all("div", class_="browse2-result-description collapsible-content")[0].get_text().strip()
            except:
                description = "-"
                
            # check if dataset provides category
            try:
                category = dataset_soup.find_all("a", class_="browse2-result-category browse2-result-header-section")[0].get_text()
            except:
                category = "-"
                
            # Generate url for API csv download
            acces_ids = link.split('/')[len(link.split('/'))-1]
            datasetUrl = baseURL_download + acces_ids + ".csv"

            # OPTIONAL: check if the url works by making a request
            # status = csv => implies the link works and csv can be downloaded
            # if status is different csv can't be downloaded
            # it can be because the resource is not csv (map, ...) or because API is broken
            status = "-"
            if(checkStatus):
                x = requests.get(datasetUrl)
                status = x.status_code
            
            retrievedData.append([title, description, category, '-', SOURCE, link, datasetUrl, status, ORIGIN])

        print("  - Pages scrapped: ", i)

        # Stop to avoid web overload
        time.sleep(1.5)
    
    catalog_columns = ['title', 'description', 'category', 'date_published', 'source', 'web_url', 'download_url', 'status', 'origin']
    catalog = pd.DataFrame(retrievedData, columns = catalog_columns)

    #catalog.to_csv("../data/catalog_hospitalet.csv", index=False)
    return catalog



