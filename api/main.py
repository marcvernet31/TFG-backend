from functions import *
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


"""
Very fast API with FastAPI

Returns list of ids ordered by similariyt
    /similar/{itemId}

Returns information about specific item
    /item/{itemId}

Returns list of all dataset information
    /catalog

Execute:
    $> uvicorn main:app --reload
    
"""

app = FastAPI()

origins = {
    "http://localhost",
    "http://localhost:3000",
}


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/similar/{itemId}")
async def similarService(itemId):
    response = similar(itemId)
    return{"message": response}


@app.get("/item/{itemId}")
async def retrieveItemService(itemId):
    response = retrieveItem(itemId)
    return {"message": response}


@app.get("/catalog")
async def catalogService():
    response = catalog()
    return {"message": response}


# Frontend elements
@app.get("/frontend/MainPage")
async def MainPageService():
    response = MainPage()
    return {"message": response}

@app.get("/frontend/Catalog")
async def MainPageService():
    response = Catalog()
    return {"message": response}

@app.get("/frontend/DataSource/{source}")
async def DataSourceService(source):
    response = DataSource(source)
    return {"message": response}
