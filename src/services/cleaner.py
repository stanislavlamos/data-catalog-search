from openai import OpenAI
import os
from dotenv import load_dotenv
import shutil
from pathlib import Path
from src.db.graph_db import GraphDb
from src.sparql_queries import drop_named_graphs_graphdb


load_dotenv()

def clean_openai_files():
    client = OpenAI()
    files = client.files.list()

    for file in files.data:
        file_id = file.id
        print(f"Deleting file: {file_id} ({file.filename})")
        client.files.delete(file_id)

def clean_tmp_folder():
    project_dir = Path(__file__).resolve().parent.parent.parent
    data_path = os.path.join(project_dir, "data", "nkod")
    tmp_dir = os.path.join(data_path, "tmp")
    shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"Cleaned temporary folder: {tmp_dir}")

def clean_distributions_folder():
    project_dir = Path(__file__).resolve().parent.parent.parent
    data_path = os.path.join(project_dir, "data", "nkod")
    tmp_dir = os.path.join(data_path, "distributions")
    shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"Cleaned distributions folder: {tmp_dir}")

def clean_openai_vector_store():
    client = OpenAI()
    stores = client.vector_stores.list(limit=100).data

    for store in stores:
        client.vector_stores.delete(store.id)
        print(f"Deleted vector store: {store.name or store.id}.")

def clean_named_graphs_in_graphdb(catalog_name: str = "nkod"):
    graph_db = GraphDb(catalog_name)
    res = graph_db.update_sparql_graphdb(drop_named_graphs_graphdb)

    print("Deleted named graphs in GraphDb repository.")
