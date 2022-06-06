The back-end is fully written in Python, so the only requirements for it  
are having installed Python itself (I personally used version 3.9), and the required  
libraries.  
Because of the code needs quite a lot of time to do the initial setup and be able  
to see the results, in the repository there’s attached a working test version already  
populated with data compressed in a zip file. This version is recommended to use  
for testing purposes, and only needs to be uncompressed and after that run the api  
command.  
Install code from the github repository and access the home folder. All the following  
commands after installation are assumed to be executed from the home directory.  
```
>  git clone https://github.com/marcvernet31/TFG-backend.git  
>  cd TFG-backend  
```

Execute the scraper scripts to generate and populate the catalog from the datasets  
available in Barcelona and Hospitalet portals.  
```
>  python3 scrappers/generateCatalog.py  
```
Calculate the similarity based on text descriptions for all the dataset pairs in the  
catalog.
```  
> python3 text-similarity/similarityMatrices.py  
```
Personally, I had many troubles installing the python library scikit-learn on my work  
computer (Apple M1) and I ended up having to install the library through a Conda  
environment. In that case, the command used is instead:  
```
> conda run -n <env-name> python3 text-similarity/similarityMatrices.py  
```
The next step is to execute the script to extract the column values for every dataset  
in the catalog and calculate the profiles.  This operation is very slow, because it  
needs to individually download every dataset in the catalog, check that the format  
is correct and calculate the profiles for individual columns. The long execution time
