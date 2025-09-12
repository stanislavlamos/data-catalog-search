get_keywords_czech_nkod = """
    SELECT dataset_uri, keywords_cs FROM {table_name}
"""

get_keywords_english_nkod = """
    SELECT dataset_uri, keywords_en FROM {table_name}
"""

get_descriptions_czech_nkod = """
    SELECT dataset_uri, description_cs FROM {table_name}
"""

get_descriptions_english_nkod = """
    SELECT dataset_uri, description_en FROM {table_name}
"""

get_titles_english_nkod = """
    SELECT dataset_uri, title_en FROM {table_name}
"""

get_titles_czech_nkod = """
    SELECT dataset_uri, title_cs FROM {table_name}
"""
