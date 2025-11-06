# Data Catalog Search


## Run project locally
1. Create `.env` file in the project root directory and add your API keys:
```env
OPENAI_API_KEY=
API_BASE_URL= http://127.0.0.1:8000
```

2. Install dependencies
```shell
make setup
```

3. Start BE app
```shell
make start_be
```

4. Start FE app
```shell
make start_fe
```

Then you can open the app at:
http://localhost:8501 


## Demo notebooks
Useful demo Jupyter notebooks included in this repository:

- [experiments_sparql_generation.ipynb](experiments_sparql_generation.ipynb) — Embeddings generation and vector index building (sentence-transformers / FAISS examples).
