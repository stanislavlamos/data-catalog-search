import re, unicodedata
from bs4 import BeautifulSoup
import numpy as np
from typing import Generator


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

    for dataset_uri, item in sql_output:
        properties = []
        if item is not None:
            properties = item.split(';_; ')
        split_output.append(
            {
                "dataset_uri": dataset_uri,
                properties_key: properties
            }
        )

    return split_output


def split_descs_or_titles_sql_output(sql_output: list, properties_key: str) -> list[dict]:
    split_output = []

    for dataset_uri, desc in sql_output:
        if desc is not None:
            split_output.append(
                {
                    "dataset_uri": dataset_uri,
                    properties_key: desc
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
        dataset_uri = {"dataset_uri": item["dataset_uri"]}
        keywords = [strip_text(to_lower(kw)) for kw in item[properties_key]]
        cur_ids = [f"id_kw{idx}_{i}" for i in range(len(keywords))]
        cur_metadatas = [dataset_uri.copy() for i in range(len(keywords))]
        texts.extend(keywords)
        metadatas.extend(cur_metadatas)
        ids.extend(cur_ids)

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
        metadatas.extend(dataset_uri)
        ids.extend(cur_id)

    return texts, ids, metadatas


def batch_list(input_list: list, batch_size: int) -> Generator[list, None, None]:
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]

