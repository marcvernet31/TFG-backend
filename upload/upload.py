import json
import argparse
import pandas as pd
from tinydb import TinyDB, Query


# Update MainPage based on database
def updateMainPage():
    # Init database
    db = TinyDB("./data/catalog.json")

    with open('./api/frontend/MainPage.json') as json_file:
        MainPage = json.load(json_file)

    # Update list of unique dataset categories
    uniqueCategories = list(set([x['category'] for x in db.all()]))
    newCategories = []
    for category in uniqueCategories:
        newCategories.append({
            'name': category, 
            'amount': len(db.search(Query().category == category))
        })
    MainPage['category'] = newCategories


    # Update amount (count of datasets by origin)
    for origin in MainPage["origin"]:
        databaseName = origin["databaseName"]
        amount = len(db.search(Query().origin == databaseName))
        origin['amount'] = amount
            
    # save changes
    with open('./api/frontend/MainPage.json', 'w') as f:
        json.dump(MainPage, f, ensure_ascii=False)


# Update Catalog based on database
def updateCatalog():
    # Init database
    db = TinyDB("./data/catalog.json")

    with open('./api/frontend/Catalog.json') as json_file:
        Catalog = json.load(json_file)

    # Update list of unique dataset categories
    uniqueCategories = list(set([x['category'] for x in db.all()]))
    newCategories = []
    for category in uniqueCategories:
        newCategories.append(category)
    Catalog['categories'] = newCategories

    # Update list of origins
    uniqueOrigins = list(set([x['origin'] for x in db.all()]))
    Catalog["origins"] = uniqueOrigins

    # save changes
    with open('./api/frontend/Catalog.json', 'w') as f:
        json.dump(Catalog, f, ensure_ascii=False)
        

# Post information regarding new data source on DataSource
def newDataSource(databaseIdentifier, forntendIdentifier, title, description, api):
    
    # Init database
    db = TinyDB("./data/catalog.json")

    with open('./api/frontend/DataSources.json') as json_file:
        DataSources = json.load(json_file)

    DataSources[databaseIdentifier] = {
            "identifier": forntendIdentifier,
            "title": title,
            "description": description,
            "amount": len(db.search(Query().origin == databaseIdentifier)),
            "api": api,
            "image": "",
            "imageText": "main image description",
            "linkText": "Continue reading…"
          }

    # save changes
    with open('./api/frontend/DataSources.json', 'w') as f:
        json.dump(DataSources, f, ensure_ascii=False)
        
        
# Upload new data source to MainPage json
def uploadToMainPage(config):
    newSource = {
        "title": config["title"],
        "sourceId": config["databaseIdentifier"],
        "databaseName": config["frontendIdentifier"],
        "amount": 0,
        "description": config["shortDescription"],
        "image": "",
        "imageLabel": ""
    }

    with open('./api/frontend/MainPage.json') as json_file:
        MainPage = json.load(json_file)
    alreadyContained = False
    for element in MainPage["origin"]:
        if element['sourceId'] == newSource['sourceId']:
            alreadyContained = True
    if not alreadyContained: MainPage["origin"].append(newSource)

    # save changes
    with open('./api/frontend/MainPage.json', 'w') as f:
        json.dump(MainPage, f, ensure_ascii=False)


## Upload new datasets to database and update frontend jsons
# packet: Folder with specifications for upload
def uploadPacket(packet):

    ### Upload new datasets to database ####
    # Init database
    db = TinyDB("./data/catalog.json")
    dataset = pd.read_csv(f"upload/uploadPackets/{packet}/newData.csv")
    for index, row in dataset.iterrows():
        db.insert({
            "title": row["title"],
            "description": row["description"],
            "category": row["category"],
            "date_published": row["date_published"],
            "source": row["source"],
            "web_url": row["web_url"],
            "download_url": row["download_url"],
            "status": row["source"],
            "origin": row["origin"]
        })
    print("-- New Data uploaded to database")


    #### Update json files that populate the frontend ####
    with open(f"upload/uploadPackets/{packet}/config.json") as json_file:
        config = json.load(json_file)
    
    uploadToMainPage(config)
    print("-- New Data uploaded to MainPage.json")
    newDataSource(config["databaseIdentifier"], config["frontendIdentifier"], config["title"], config["description"], config["api"])
    print("-- DataSource.json is updated")
    updateCatalog()
    print("-- Catalog.json is updated")
    updateMainPage()
    print("-- MainPage.json is updated")



def main():
    # Flags per al terminal
    parser = argparse.ArgumentParser()
    parser.add_argument("-packet", "--packet", help="True: save KPI matrix as csv locally (False: default)")
    args = parser.parse_args()

    packet = args.packet
    uploadPacket(packet)


if __name__ == "__main__":
    main()