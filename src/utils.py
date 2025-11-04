import re, unicodedata
from bs4 import BeautifulSoup
import numpy as np
from typing import Generator
import random
import json
from src.schemas.schemas import DatasetSelectionOutput
import pandas as pd


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


def split_keywords_sql_output(sql_output: list, properties_key: str) -> list[dict]:
    split_output = []

    for dataset_uri, item, dataset_title, has_rdf_distribution in sql_output:
        properties = []
        if item is not None:
            properties = item.split(';_; ')
        split_output.append(
            {
                "dataset_uri": dataset_uri,
                properties_key: properties,
                "dataset_title": dataset_title,
                "has_rdf_distribution": has_rdf_distribution
            }
        )

    return split_output


def split_descs_sql_output(sql_output: list, properties_key: str) -> list[dict]:
    split_output = []

    for dataset_uri, desc, dataset_title, has_rdf_distribution in sql_output:
        if desc is not None and len(desc) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    properties_key: desc,
                    "dataset_title": dataset_title,
                    "has_rdf_distribution": has_rdf_distribution
                }
            )

    return split_output


def split_titles_sql_output(sql_output: list, properties_key: str) -> list[dict]:
    split_output = []

    for dataset_uri, desc, has_rdf_distribution in sql_output:
        if desc is not None and len(desc) != 0:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    properties_key: desc,
                    "has_rdf_distribution": has_rdf_distribution
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
        metadata = {"dataset_uri": item["dataset_uri"], "dataset_title": str(item["dataset_title"]), "has_rdf_distribution": item["has_rdf_distribution"]}
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
        metadata = {"dataset_uri": item["dataset_uri"], "dataset_title": str(item["dataset_title"]), "has_rdf_distribution": item["has_rdf_distribution"]}
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
        metadata = {"dataset_uri": item["dataset_uri"], "dataset_title": str(item[properties_key]), "has_rdf_distribution": item["has_rdf_distribution"]}
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

def parse_chroma_output(query_result: dict[str, list[list[dict]]]) -> list[dict]:
    print("query_result:", query_result)
    docs = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    scores = query_result["distances"][0]
    output = []
    
    for doc, metadata_dict, score in zip(docs, metadatas, scores):
        metadata_dict["score"] = score
        metadata_dict["doc"] = doc
        output.append(metadata_dict)

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
