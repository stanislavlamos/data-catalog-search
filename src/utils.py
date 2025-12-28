import ast
import re, unicodedata
from bs4 import BeautifulSoup
import numpy as np
from typing import Generator
import random
import json
from src.schemas.schemas import DatasetSelectionOutput
import pandas as pd
import urllib.parse
import os
import glob


def strip_text(txt: str) -> str:
    return txt.strip()

def to_lower(txt: str) -> str:
    return txt.lower()

def remove_html(txt: str) -> str:
    return BeautifulSoup(txt, "html.parser").get_text()

def normalize_unicode(txt: str) -> str:
    return unicodedata.normalize("NFC", txt)

def replace_newlines_and_tabs(txt: str) -> str:
    return re.sub(r"\s+", " ", txt)

def clean_text(txt: str) -> str:
    stripped = strip_text(txt)
    lower = to_lower(stripped)
    html_removed = remove_html(lower)
    unicode_removed = normalize_unicode(html_removed)
    cleaned_txt = replace_newlines_and_tabs(unicode_removed)

    return cleaned_txt

def split_keywords_cs_sql_output(sql_output: list) -> list[dict]:
    split_output = []
    
    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if keywords_cs is not None and len(keywords_cs) != 0:
            properties = keywords_cs.split(';_; ')
            keywords_en = "None" if keywords_en is None else keywords_en.split(';_; ')
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": properties,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_keywords_en_sql_output(sql_output: list) -> list[dict]:
    split_output = []
    
    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if keywords_en is not None and len(keywords_en) != 0:
            properties = keywords_en.split(';_; ')
            keywords_cs = "None" if keywords_cs is None else keywords_cs.split(';_; ')
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": properties,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_descs_cs_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if description_cs is not None and len(description_cs) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_descs_en_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if description_en is not None and len(description_en) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_titles_cs_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if title_cs is not None and len(title_cs) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_publishers_cs_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if publisher_cs is not None and len(publisher_cs) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_publishers_en_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if publisher_en is not None and len(publisher_en) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_titles_en_sql_output(sql_output: list) -> list[dict]:
    split_output = []

    for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_output:
        if title_en is not None and len(title_en) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    "title_cs": title_cs,
                    "title_en": title_en,
                    "description_cs": description_cs,
                    "description_en": description_en,
                    "keywords_cs": keywords_cs,
                    "keywords_en": keywords_en,
                    "themes": themes,
                    "has_rdf_distribution": has_rdf_distribution,
                    "publisher_en": publisher_en,
                    "publisher_cs": publisher_cs,
                    "matched_substring": matched_substring
                }
            )

    return split_output

def split_themes_sql_output(sql_output: list, properties_key: str) -> list[dict]:
    split_output = []

    for theme_name, property in sql_output:
        if property is not None and len(property) != 0:
            split_output.append(
                {
                    "theme_name": theme_name,
                    properties_key: property
                }
            )

    return split_output

def print_keywords_stats(split_sql_output: list[dict], properties_key: str, language: str) -> None:
    n_keywords = []

    for item in split_sql_output:
        n_keywords.append(len(item[properties_key]))

    mean_keywords = np.array(n_keywords).mean()
    print(f"Mean number of {language} keywords: {mean_keywords}")

def print_titles_stats(split_sql_output: list[dict], properties_key: str, language: str) -> None:
    n_titles = [0 if title[properties_key] is None else 1 for title in split_sql_output]
    mean_titles = np.array(n_titles).mean()
    print(f"Mean number of {language} titles that are not None: {mean_titles}")

def print_descs_stats(split_sql_output: list[dict], properties_key: str, language: str) -> None:
    n_descs = [0 if desc[properties_key] is None else 1 for desc in split_sql_output]
    mean_descs = np.array(n_descs).mean()
    print(f"Mean number of {language} descriptions that are not None: {mean_descs}")

def prepare_nkod_keywords_for_chromadb(keywords_from_sql: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(keywords_from_sql):
        metadata = {
            "dataset_uri": item.get("dataset_uri", "None") if item.get("dataset_uri", "None") is not None else "None",
            "title_cs": item.get("title_cs", "None") if item.get("title_cs", "None")  is not None else "None",
            "title_en": item.get("title_en", "None") if item.get("title_en", "None") is not None else "None",
            "description_cs": item.get("description_cs", "None") if item.get("description_cs", "None") is not None else "None",
            "description_en": item.get("description_en", "None") if item.get("description_en", "None") is not None else "None",
            "keywords_cs": ';_; '.join(item["keywords_cs"]) if ';_; '.join(item.get("keywords_cs", "None")) is not None else "None",
            "keywords_en": ';_; '.join(item["keywords_en"]) if ';_; '.join(item.get("keywords_en", "None")) is not None else "None",
            "themes": item.get("themes", "None") if item.get("themes", "None") is not None else "None",
            "has_rdf_distribution": item.get("has_rdf_distribution", "None") if item.get("has_rdf_distribution", "None") is not None else "None",
            "publisher_en": item.get("publisher_en", "None") if item.get("publisher_en", "None") is not None else "None",
            "publisher_cs": item.get("publisher_cs", "None") if item.get("publisher_cs", "None") is not None else "None",
            "matched_substring": item.get("matched_substring", "None") if item.get("matched_substring", "None") is not None else "None"
        }
        keywords = [strip_text(to_lower(kw)) for kw in item[properties_key]]

        if len(keywords) == 0:
            continue

        cur_ids = [f"id_kw{idx}_{i}" for i in range(len(keywords))]
        cur_metadatas = [metadata.copy() for i in range(len(keywords))]
        texts.extend(keywords)
        metadatas.extend(cur_metadatas)
        ids.extend(cur_ids)
    
    return texts, ids, metadatas

def prepare_nkod_descs_for_chromadb(sql_output: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(sql_output):
        metadata = {
            "dataset_uri": item.get("dataset_uri", "None") if item.get("dataset_uri", "None") is not None else "None",
            "title_cs": item.get("title_cs", "None") if item.get("title_cs", "None")  is not None else "None",
            "title_en": item.get("title_en", "None") if item.get("title_en", "None") is not None else "None",
            "description_cs": item.get("description_cs", "None") if item.get("description_cs", "None") is not None else "None",
            "description_en": item.get("description_en", "None") if item.get("description_en", "None") is not None else "None",
            "keywords_cs": item.get("keywords_cs", "None") if item.get("keywords_cs", "None") is not None else "None",
            "keywords_en": item.get("keywords_en", "None") if item.get("keywords_en", "None") is not None else "None",
            "themes": item.get("themes", "None") if item.get("themes", "None") is not None else "None",
            "has_rdf_distribution": item.get("has_rdf_distribution", "None") if item.get("has_rdf_distribution", "None") is not None else "None",
            "publisher_en": item.get("publisher_en", "None") if item.get("publisher_en", "None") is not None else "None",
            "publisher_cs": item.get("publisher_cs", "None") if item.get("publisher_cs", "None") is not None else "None",
            "matched_substring": item.get("matched_substring", "None") if item.get("matched_substring", "None") is not None else "None"
        }
        text = strip_text(to_lower(item[properties_key]))
        cur_id = f"id_item_{idx}"
        texts.append(text)
        metadatas.append(metadata)
        ids.append(cur_id)

    return texts, ids, metadatas

def prepare_nkod_titles_for_chromadb(sql_output: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(sql_output):
        metadata = {
            "dataset_uri": item.get("dataset_uri", "None") if item.get("dataset_uri", "None") is not None else "None",
            "title_cs": item.get("title_cs", "None") if item.get("title_cs", "None")  is not None else "None",
            "title_en": item.get("title_en", "None") if item.get("title_en", "None") is not None else "None",
            "description_cs": item.get("description_cs", "None") if item.get("description_cs", "None") is not None else "None",
            "description_en": item.get("description_en", "None") if item.get("description_en", "None") is not None else "None",
            "keywords_cs": item.get("keywords_cs", "None") if item.get("keywords_cs", "None") is not None else "None",
            "keywords_en": item.get("keywords_en", "None") if item.get("keywords_en", "None") is not None else "None",
            "themes": item.get("themes", "None") if item.get("themes", "None") is not None else "None",
            "has_rdf_distribution": item.get("has_rdf_distribution", "None") if item.get("has_rdf_distribution", "None") is not None else "None",
            "publisher_en": item.get("publisher_en", "None") if item.get("publisher_en", "None") is not None else "None",
            "publisher_cs": item.get("publisher_cs", "None") if item.get("publisher_cs", "None") is not None else "None",
            "matched_substring": item.get("matched_substring", "None") if item.get("matched_substring", "None") is not None else "None"
        }
        text = strip_text(to_lower(item[properties_key]))
        cur_id = f"id_item_{idx}"
        texts.append(text)
        metadatas.append(metadata)
        ids.append(cur_id)

    return texts, ids, metadatas

def prepare_nkod_publishers_for_chromadb(sql_output: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(sql_output):
        metadata = {
            "dataset_uri": item.get("dataset_uri", "None") if item.get("dataset_uri", "None") is not None else "None",
            "title_cs": item.get("title_cs", "None") if item.get("title_cs", "None")  is not None else "None",
            "title_en": item.get("title_en", "None") if item.get("title_en", "None") is not None else "None",
            "description_cs": item.get("description_cs", "None") if item.get("description_cs", "None") is not None else "None",
            "description_en": item.get("description_en", "None") if item.get("description_en", "None") is not None else "None",
            "keywords_cs": item.get("keywords_cs", "None") if item.get("keywords_cs", "None") is not None else "None",
            "keywords_en": item.get("keywords_en", "None") if item.get("keywords_en", "None") is not None else "None",
            "themes": item.get("themes", "None") if item.get("themes", "None") is not None else "None",
            "has_rdf_distribution": item.get("has_rdf_distribution", "None") if item.get("has_rdf_distribution", "None") is not None else "None",
            "publisher_en": item.get("publisher_en", "None") if item.get("publisher_en", "None") is not None else "None",
            "publisher_cs": item.get("publisher_cs", "None") if item.get("publisher_cs", "None") is not None else "None",
            "matched_substring": item.get("matched_substring", "None") if item.get("matched_substring", "None") is not None else "None"
        }
        text = strip_text(to_lower(item[properties_key]))
        cur_id = f"id_item_{idx}"
        texts.append(text)
        metadatas.append(metadata)
        ids.append(cur_id)

    return texts, ids, metadatas

def prepare_nkod_themes_properties_for_chromadb(sql_output: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(sql_output):
        dataset_uri = {"theme_name": item["theme_name"]}
        text = strip_text(to_lower(item[properties_key]))
        cur_id = f"id_item_{idx}"
        texts.append(text)
        metadatas.append(dataset_uri)
        ids.append(cur_id)

    return texts, ids, metadatas

def prepare_nkod_titles_and_descs_for_chromadb(sql_output: list[dict], properties_key: str) -> tuple[list[str], list[str], list[dict]]:
    texts = []
    metadatas = []
    ids = []

    for idx, item in enumerate(sql_output):
        dataset_uri = {"dataset_uri": item["dataset_uri"]}
        text = strip_text(to_lower(item[properties_key]))
        cur_id = f"id_item_{idx}"
        texts.append(text)
        metadatas.append(dataset_uri)
        ids.append(cur_id)

    return texts, ids, metadatas

def batch_list(input_list: list, batch_size: int) -> Generator[list, None, None]:
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]

def get_n_random_list_idxs(inp_lst_len: int, n: int, seed: int = 15) -> list:
    random.seed(seed)
    return random.sample(range(inp_lst_len), n)

def save_list_as_jsonl(data: list, fpath: str) -> None:
    with open(fpath, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Saved {len(data)} entries to {fpath}")

def split_dataset_creation_sql_output(sql_output: list, language: str) -> list[dict]:
    split_output = []

    for dataset_uri, title, desc in sql_output:
        if desc is not None and len(desc) != 0 and title is not None and len(title) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    f"title_{language}": title,
                    f"description_{language}": desc
                }
            )

    return split_output

def parse_chroma_output(query_result: dict[str, list[list[dict]]], matched_on: str, return_df: bool = False) -> list[dict] | pd.DataFrame:
    docs = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    scores = query_result["distances"][0]
    output = []
    
    for doc, metadata_dict, score in zip(docs, metadatas, scores):
        metadata_dict["score"] = score
        metadata_dict["doc"] = doc
        metadata_dict["matched_on"] = matched_on
        output.append(metadata_dict)

    if return_df:
        return pd.DataFrame(output)

    return output

def get_uris_from_chroma_query(query_result: dict[str, list[list[dict]]], metadata_key: str = "dataset_uri") -> list[str]:
    # TODO: nahradit pomoci parse_chroma_output
    print("query_result:", query_result)
    docs = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    scores = query_result["distances"][0]
    output = [metadata_dict[metadata_key] for metadata_dict in results]

    return output

def get_docs_and_scores_from_chroma_query(query_result_metadata: list[list[dict]], query_result_scores: list[list[float]], metadata_key: str) -> list[tuple[float, str]]:
    docs = query_result_metadata[0]
    scores = query_result_scores[0]

    return list(zip(scores, docs))

def load_jsonl_to_list(fpath: str) -> list[dict]:
    data = []
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))

    return data

def merge_chromadb_docs_with_metadatas(query_result: dict) -> list[dict]:
    docs = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]

    return [{"title": s, "dataset_uri": v} for s, d in zip(docs, metadatas) for k, v in d.items()]

def get_relevance_score(output: DatasetSelectionOutput, target_uri: str) -> float:
    for dataset in output.datasets:
        if dataset.uri == target_uri:
            return dataset.relevance_score
    return 0.0

def get_intersection(input_lists: list[list]) -> list:
    return list(set(input_lists[0]).intersection(*map(set, input_lists[1:])))

def get_overlap_info(inp_lst: list, out_lst: list) -> str:
    overlap = []
    positions = []

    for item in inp_lst:
        if item in out_lst:
            pos = out_lst.index(item)
            overlap.append(item)
            positions.append(pos)

    count = len(overlap)

    if count == 0:
        return f"False -> 0/0 present | positions: []"
    else:
        return f"True -> {count}/{len(inp_lst)} present | positions: {positions}"

def merge_lst_with_tuple_lst(lst: list, tpl_lst: list[tuple]) -> list[dict]:
    merged = []

    for item, tpl in zip(lst, tpl_lst):
        merged.append({"doc": tpl[1], "dataset_uri": item})

    return merged

def delete_sparql_backticks(inp_str: str) -> str:
    return inp_str.replace("```sparql", "").replace("```", "")

def intersect_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, left_on: str, right_on: str) -> pd.DataFrame:
    return pd.merge(df1, df2, left_on=left_on, right_on=right_on, how='inner')

def dir_name_from_uri(dataset_uri: str) -> str:
    return dataset_uri.rstrip('/').rsplit('/', 1)[-1]

def encode_graphdb_statements(statement: str) -> str:
    return urllib.parse.quote(statement, safe='')

def create_named_graph_uri(graph_iri: str):
    return f"http://example.org/{graph_iri}"

def find_files_with_prefix(directory_path, prefix) -> str | None:
    search_pattern = os.path.join(directory_path, f"{prefix}*")
    found_files = glob.glob(search_pattern)
    
    if not found_files:
        return None
    
    return os.path.basename(found_files[0])

def list_folders(search_path: str) -> list:
    folder_names = []

    for item_name in os.listdir(search_path):
        full_path = os.path.join(search_path, item_name)
        
        if os.path.isdir(full_path):
            folder_names.append(item_name)

    return folder_names

def check_dir_status_os(dir_path: str) -> bool:
    if not os.path.exists(dir_path):
        return False

    elif not os.listdir(dir_path):
        return False
    
    else:
        return True

def format_few_shot_examples(few_shot_list: list[dict]) -> str:
    formatted_examples = []

    for idx, example in enumerate(few_shot_list, start=1):
        question = example.get("question")
        query = example.get("sparql_query", "").strip()

        formatted_example = f"""### Example {idx}
        **Question:**
        {question}
        
        **Correct Output:**
        ```sparql
        {query}
        ```
        """
        formatted_examples.append(formatted_example)

    return "\n\n".join(formatted_examples)

def get_few_shot_fnames(matched_substring_lst: list) -> list[str]:
    results_list = []
    for input_str in matched_substring_lst:
        first_letters = []
        words = input_str.split()

        for word in words:
            if word:
                first_letters.append(word[0].replace('ú', 'u'))

        result_str = "_".join(first_letters)
        results_list.append(f"few_shot_queries_{result_str}.json")

    return results_list

def load_multiple_jsons_to_list(fnames: list[str]) -> list[dict]:
    results = []

    for fname in fnames:
        with open(fname, 'r') as f:
            data = json.load(f)
            results.extend(data)

    return results

def format_schemas_for_prompt(schemas: list[str], formats: list[str]) -> str:
    if not schemas:
        return ""

    formatted_blocks = []
    for i, schema in enumerate(schemas):
        block = f"### Schema {i+1}\n{schema.strip()}, format: {formats[i]}\n"
        formatted_blocks.append(block)

    return "\n".join(formatted_blocks)

def format_publishers_or_titles(inp_lst: list[str]) -> str:
    if not inp_lst:
        return ""
    return "\n".join(inp_lst)

def format_input_for_reranker(df: pd.DataFrame) -> tuple[list, list]:
    uris = df["dataset_uri"].tolist()
    formated_df = df["title_cs"].astype(str) + "\n" + df["publisher_cs"].astype(str) + '\n' + df["description_cs"].astype(str)
    return formated_df.tolist(), uris

def get_indexes_from_cohere_reranker(response: dict) -> list[int]:
    return [r["index"] for r in response["results"]]

def sparql_json_to_df(inp_dict: dict) -> pd.DataFrame:
    bindings = inp_dict.get("results", {}).get("bindings", [])

    rows = []
    for row in bindings:
        rows.append({var: val.get("value") for var, val in row.items()})

    df = pd.DataFrame(rows)
    return df

def count_bindings(data: dict) -> int:
    return len(data.get("results", {}).get("bindings", []))

def count_unique_per_var(data: dict) -> dict:
    bindings = data.get("results", {}).get("bindings", [])
    vars_ = data.get("head", {}).get("vars", [])

    result_sets = {var: set() for var in vars_}

    for binding in bindings:
        for var in vars_:
            if var in binding and "value" in binding[var]:
                result_sets[var].add(binding[var]["value"])

    return {var: len(values) for var, values in result_sets.items()}

def count_sparql_constructs(query: str) -> dict:
    q = query.upper()

    counts = {
        "PREFIX": len(re.findall(r"\bPREFIX\b", q)),
        "UNION": len(re.findall(r"\bUNION\b", q)),
        "OPTIONAL": len(re.findall(r"\bOPTIONAL\b", q)),
        "FILTER": len(re.findall(r"\bFILTER\b", q)),
    }

    return counts

def get_sparql_stats(sparql_query: str, res: dict | list):
    if isinstance(res, list):
        print("Malformed query, please reformat your query.")
    else:
        print(f"Bindings len: {count_bindings(res)}")
        print(f"Bindings per var: {count_unique_per_var(res)}")
        print(f"SPARQL constructs: {count_sparql_constructs(sparql_query)}")
        print(f"SPARQL len: {len(sparql_query)}")

def match_uris(uris: list[str], dicts: list[dict], uri_key="dataset_uri") -> dict:
    results = {}
    for uri in uris:
        found = False
        for idx, d in enumerate(dicts):
            if d.get(uri_key) == uri:
                results[uri] = (True, idx)
                found = True
                break
        if not found:
            results[uri] = (False, None)
            
    return results
