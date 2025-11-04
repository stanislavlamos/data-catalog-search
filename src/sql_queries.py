get_keywords_czech_nkod = """
    SELECT dataset_uri, keywords_cs, title_cs, has_rdf_distribution FROM {table_name}
"""

get_keywords_english_nkod = """
    SELECT dataset_uri, keywords_en, title_en, has_rdf_distribution FROM {table_name}
"""

get_descriptions_czech_nkod = """
    SELECT dataset_uri, description_cs, title_cs FROM {table_name}
"""

get_descriptions_english_nkod = """
    SELECT dataset_uri, description_en, title_en FROM {table_name}
"""

get_titles_english_nkod = """
    SELECT dataset_uri, title_en, has_rdf_distribution FROM {table_name}
"""

get_titles_czech_nkod = """
    SELECT dataset_uri, title_cs, has_rdf_distribution FROM {table_name}
"""

get_titles_and_descs_czech_nkod = """
    SELECT dataset_uri, title_cs, description_cs, has_rdf_distribution FROM {table_name}
"""

get_titles_and_descs_english_nkod = """
    SELECT dataset_uri, title_en, description_en, has_rdf_distribution FROM {table_name}
"""

get_themes_labels_english_nkod = """
    SELECT theme_name, theme_label_en FROM {table_name}
"""

get_themes_labels_czech_nkod = """
    SELECT theme_name, theme_label_cz FROM {table_name}
"""

get_themes_definitions_english_nkod = """
    SELECT theme_name, theme_definition_en FROM {table_name}
"""

get_themes_definitions_czech_nkod = """
    SELECT theme_name, theme_definition_cz FROM {table_name}
"""

get_titles_from_uri_czech_nkod = """
    SELECT title_cs FROM {table_name} WHERE dataset_uri = '{dataset_uri}'
"""

get_titles_from_uri_english_nkod = """
    SELECT title_en FROM {table_name} WHERE dataset_uri = '{dataset_uri}'
"""
