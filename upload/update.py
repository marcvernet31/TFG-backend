import json
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


def main():
    updateCatalog()
    updateMainPage()


if __name__ == "__main__":
    main()