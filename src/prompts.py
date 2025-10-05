# You are a language classifier. Classify any text as Czech, English, or Other. If the text contains a mixture of Czech and English, or any other language, classify it as Other. Do not take entities and concrete names into account, such as: cities, names, places, food etc...
language_detection_system = {
    "gpt-5": "You are a helpful assistant, classify the given text as 'Czech', 'English', or 'Other'. If the text contains a mix of Czech and English, or any language other than Czech or English, classify it as 'Other'. Do not take entities and concrete names into account, such as: cities, names, places, food etc...",
    "gpt-4.1": "You are a helpful assistant, classify the input text as one of the following: Czech, English, or Other. If the text is a mixture of Czech, English, or any other languages, classify it as Other. Do not take entities and concrete names into account, such as: cities, names, places, food etc...",
    "gpt-3o": "You are a helpful assistant, classify the input text as 'Czech', 'English', or 'Other'. If the text contains a mix of languages, select 'Other'. Return your answer as a single word. Do not take entities and concrete names into account, such as: cities, names, places, food etc..."
}

language_detection_user = {
    "gpt-5": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Official bulletin board Ostrava - Trebovice" → english
        "Official bulletin board Rožnov pod Radhoštěm" → english
        "ZPS obec Studenec" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text: \n
        {text}
        \n
    """,

    "gpt-4.1": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Official bulletin board Ostrava - Trebovice" → english
        "Official bulletin board Rožnov pod Radhoštěm" → english
        "ZPS obec Studenec" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text: \n
        {text}
        \n
    """,

    "gpt-3o": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Official bulletin board Ostrava - Trebovice" → english
        "Official bulletin board Rožnov pod Radhoštěm" → english
        "ZPS obec Studenec" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text: \n
        {text}
        \n
    """
}

timeframe_detection_system = {
    "gpt-5": """
        Role: Build a helpful assistant to extract explicit timeframes from user queries.

        Checklist (before extraction):
        - Scan for explicit timeframes (e.g., 'next week', 'last month').
        - Interpret phrases using today’s date ({today}).
        - Convert to start and end dates (ISO 8601, YYYY-MM-DD).
        - Set dates to null and timeframe to false if timeframe is ambiguous/incomplete (e.g., 'June' without year).
        - Always output valid JSON matching the schema below.
        - Validate output and self-correct if needed.
        
        Always output in JSON format using the structured schema provided.
        
        Use the system's current time zone ({today}). Output must be clear, concise, and conform strictly to the schema. Refine until a valid timeframe or no timeframe is produced.
    """,

    "gpt-4.1": "",

    "gpt-3o": ""
}

timeframe_detection_user = {
    "gpt-5": """
        Analyze the following user query for a timeframe and provide a structured JSON response:
        \n{user_query}\n
    """,

    "gpt-4.1": """
        
    """,

    "gpt-3o": """
        
    """
}

old_timeframe_detection_system = """
    You are a helpful assistant that detects timeframes in user queries.
    If a timeframe is specified (like 'next week', 'last month', 'between June 1 and June 10'),
    return the absolute start and end dates based on today's date ({today}). 
    Always output in JSON format using the structured schema provided.
"""


nkod_query_matching_dataset_simple_system = {
    "gpt-5": """
        You are a helpful assistant that generates possible user queries about NKOD datasets based on their titles and descriptions.
        
        Instructions:
        Use only the provided title and description to generate relevant queries.
        You can also look at the dataset URI for context, but do not include it in the queries.
        Generate only one query that a user might ask to qet info about this dataset.
        Take into account that the generated query has to be convertable to SPARQL.
        Queries has to simple, just take the title of the dataset and formulate it into question.
        Always output in JSON format using the structured schema provided.
        Return only the generated query, nothing else.
        The query should be in provided language (cs or en).
    """
}


nkod_query_matching_dataset_simple_user = {
    "gpt-5": """
        Generates possible user query about NKOD datasets based on the provided title and description.
        Use only the provided title and description to generate relevant queries.
        You can also look at the dataset URI for context, but do not include it in the queries.
        Take into account that the generated query has to be convertable to SPARQL.
        Queries has to simple, just take the title of the dataset and formulate it into question.
        Return only the generated query, nothing else.
        The query should be in provided language (cs or en).
        
        Language: \n
        {language}
        \n
        
        Title: \n 
        {title}
        \n
        
        Description: \n 
        {description}
        \n
        
        Dataset URI (for context only): \n 
        {dataset_uri}
        \n
    """
}


nkod_query_matching_llm_judge_system = {
    "gpt-5": """
        You are an advanced dataset recommender.
        You will be given a user query and a list of candidate datasets (Doc + URI).
        Your task is to rerank the datasets that based on how they reflect the user query.
        Consider relevance, coverage, and complementarity of the Doc field to the query from the user.
        Rank the selected datasets from most relevant to least relevant.
        Return in the provided structured format.
        Do not change the URIs or Docs.
    """
}

nkod_query_matching_llm_judge_user = {
    "gpt-5": """
        You are given a user query describing the datasets they need, and a list of candidate datasets with Doc and URIs.

        User Query:
        {user_query}
        
        Candidate Datasets:
        {datasets}
        
        Your task is to rerank the datasets based on how they satisfy the user's query.
        - Consider relevance, coverage, and complementarity.
        - Rank datasets from most relevant to least relevant.
        - Assign a relevance_score between 0 (irrelevant) and 1 (perfectly relevant).
        
        Return the output in the provided structured format.
    """
}


