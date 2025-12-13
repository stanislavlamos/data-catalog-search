install:
	pip install -r requirements.txt --break-system-packages

index_build:
	python -c "from src.services.index_data_nkod import IndexDataNkod; IndexDataNkod().create_sqls()"
	python -c "from src.services.index_data_nkod import IndexDataNkod; IndexDataNkod().index_nkod_metadata()"

generate_properties:
	python -c "from src.services.property_generator import PropertyGenerator; PropertyGenerator().generate_properties()"	

generate_few_shots:
	python -c "from src.services.few_shot_generator import FewShotGenerator; FewShotGenerator().generate_few_shots()"

start_fe:
	streamlit run app.py --server.fileWatcherType none

alter_matched_substring_df_column:
	python -c "from src.services.few_shot_generator import FewShotGenerator; FewShotGenerator().alter_matched_substring_df_column()"

start_be:
	uvicorn main:app --reload

setup_build:
	mkdir -p ./data/nkod/tmp
	find ./data/nkod -type d -name "*-*" -exec rm -r {} +
	rm -f ./data/nkod/chroma.sqlite3
	rm -f ./data/nkod/chroma.sqlite3-journal
	rm -f ./data/nkod/nkod_metadata.db
	rm -f ./data/nkod/nkod_themes.db
	make unzip_build
	make install
	make index_build

prepare_deploy:
	mkdir -p ./data/nkod/tmp
	find ./data/nkod -type d -name "*-*" -exec rm -r {} +
	rm -f ./data/nkod/chroma.sqlite3
	rm -f ./data/nkod/chroma.sqlite3-journal
	rm -f ./data/nkod/nkod_metadata.db
	rm -f ./data/nkod/nkod_themes.db
	make unzip_build
	make install
	make index_build

jsonld_to_txt:
	python -c "from src.services.jsonld_to_txt import JsonldToTxt; JsonldToTxt().generate()"	

clean_openai_files:
	python -c "from src.services.cleaner import clean_openai_files; clean_openai_files()"

clean_tmp_dir:
	python -c "from src.services.cleaner import clean_tmp_folder; clean_tmp_folder()"

clean_openai_vector_stores:
	python -c "from src.services.cleaner import clean_openai_vector_store; clean_openai_vector_store()"

clean_named_graphs_graphdb:
	python -c "from src.services.cleaner import clean_named_graphs_in_graphdb; clean_named_graphs_in_graphdb()"

create_env:
	rm -rf data_catalog_env
	python -m venv data_catalog_env

archive_build:
	cd data/nkod && zip -9r ofn_build.zip nkod_themes.csv nkod_publishers.csv nkod_ofn_metadata.csv nkod_metadata.trig nkod_metadata.csv nkod_distributions.csv nkod_distributions_queried.csv nkod_datasets.csv distributions/

create_vector_stores:
	python -c "from src.services.openai_vector_stores_creator import OpenaiVectorStoresCreator; OpenaiVectorStoresCreator().create_vector_stores()"

unzip_build:
	cd data/nkod/ && unzip ofn_build.zip