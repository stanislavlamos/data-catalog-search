from openai import OpenAI
import os
from dotenv import load_dotenv
import shutil
from pathlib import Path


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
