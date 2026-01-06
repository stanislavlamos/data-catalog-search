# Data Catalog Search
You can try our **deployed application** here:
https://data-catalog-search.onrender.com

## Run project locally
1. Create `.env` file in the project root directory and add your API keys:
```env
OPENAI_API_KEY=
API_BASE_URL=http://127.0.0.1:8000
GRAPH_DB_REPO=
GRAPH_DB_REPO_UPDATE=
GRAPH_DB_USER=
GRAPH_DB_PASSWORD=
DATA_VIEWER_URL=
CO_API_KEY=
GOOGLE_API_KEY=
```

2. Create and activate custom environment
```shell
make create_env
source data_catalog_env/bin/activate
```

3. Install dependencies
```shell
make setup_build
```

4. Start FE app
```shell
make start_fe
```

Then you can open the app at:
http://localhost:8501 


## Demo notebooks
Useful demo Jupyter notebooks included in this repository:

- [experiments_sparql_generation.ipynb](experiments_sparql_generation.ipynb) — Generation of SPARQL queries
- [experiments_query_matching.ipynb](experiments_query_matching.ipynb) — Matching of datasets
- [data_analysis.ipynb](data_analysis.ipynb) — Data analysis of our OFN dataset

