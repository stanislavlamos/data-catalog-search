install:
	pip install -r requirements.txt --break-system-packages

index:
	python index_data_nkod.py

start_fe:
	streamlit run app.py

start_be:
	uvicorn main:app --reload

setup:
	mkdir -p ./data/nkod/tmp
	mkodir -p ./data/nkod/distributions
	find ./data/nkod -type d -name "*-*" -exec rm -r {} +
	rm -f ./data/nkod/chroma.sqlite3
	rm -f ./data/nkod/chroma.sqlite3-journal
	rm -f ./data/nkod/nkod_metadata.db
	rm -f ./data/nkod/nkod_themes.db
	make install
	make index

clean_openai_files:
	python -c "from src.services.cleaner import clean_openai_files; clean_openai_files()"

clean_tmp_dir:
	python -c "from src.services.cleaner import clean_tmp_folder; clean_tmp_folder()"

clean_distributions_dir:
	python -c "from src.services.cleaner import clean_distributions_folder; clean_distributions_folder()"

clean_openai_vector_stores:
	python -c "from src.services.cleaner import clean_openai_vector_store; clean_openai_vector_store()"

create_env:
	rm -rf data_catalog_env
	python -m venv data_catalog_env
	