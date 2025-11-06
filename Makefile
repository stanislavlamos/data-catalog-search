install:
	pip install -r requirements.txt --break-system-packages

index:
	python index_data_nkod.py

start_fe:
	streamlit run app.py

start_be:
	uvicorn main:app --reload

make setup:
	make install
	make index
