# Data Catalog Search


## Run project locally
1. Create `.env` file in the project root directory and add your API keys:
```env
OPENAI_API_KEY=
API_BASE_URL= http://127.0.0.1:8000
GRAPH_DB_REPO=http://osw.felk.cvut.cz:7200/repositories/lamossta
GRAPH_DB_REPO_UPDATE=http://osw.felk.cvut.cz:7200/repositories/lamossta/statements
GRAPH_DB_USER=lamossta
GRAPH_DB_PASSWORD="S$i#9KoYNxA!cQ"
DATA_VIEWER_URL=https://data-catalog-viewer-ysmlxmu5hmhaet3xa5nkyz.streamlit.app/
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

- [experiments_sparql_generation.ipynb](experiments_sparql_generation.ipynb) — Embeddings generation and vector index building
