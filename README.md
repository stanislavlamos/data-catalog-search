# Data Catalog Search


## Run project locally
1. Create `.env` file in the project root directory and add your API keys:
```env
OPENAI_API_KEY=
API_BASE_URL= http://127.0.0.1:8000
```

2. Create and activate custom environment
```shell
./setup_env.sh
source "$ENV_NAME/bin/activate"
```

3. Install dependencies
```shell
make setup
```

4. Start BE app
```shell
make start_be
```

5. Start FE app
```shell
make start_fe
```

Then you can open the app at:
http://localhost:8501 


## Demo notebooks
Useful demo Jupyter notebooks included in this repository:

- [experiments_sparql_generation.ipynb](experiments_sparql_generation.ipynb) — Embeddings generation and vector index building
