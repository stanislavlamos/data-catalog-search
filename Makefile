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
	make install
	make index

clean_openai_files:
	python -c "from src.services.cleaner import clean_openai_files; clean_openai_files()"

clean_tmp_dir:
	python -c "from src.services.cleaner import clean_tmp_folder; clean_tmp_folder()"
