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


nkod_rag_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.
    Given one or more schemas (in JSON, JSON-LD, Turtle, XML, RDF/XML, or TriG) and a natural language query, generate a valid SPARQL query.
    """
}


nkod_rag_user = {
    "gpt-5": """
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation. 
    Use only classes and properties defined the schema(s).
    If some info in the user question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    Your task is to generate correct, efficient, and human-readable SPARQL query given:
        (1) a schema provided in RDF, JSON, XML, JSON-LD, Turtle (.ttl), or TriG (.trig) format, and 
        (2) a natural language question.
    
    Requirements:
    - Parse and interpret the provided schema(s), respecting prefixes and namespaces.
    - Use only classes and properties defined the schema(s).
    - Produce a syntactically valid and semantically consistent SPARQL query.
    - Output only the query in a markdown code block (sparql), nothing else.
    - Do not make assumptions beyond the provided schema.
    - There might be multiple schemas, handle them appropriately and connect them using common properties.
    - Do not insert any comments or explanations in the output.
    - Ensure the query is efficient and avoids unnecessary complexity.
    - Respect the language of the schemas, do not translate anything.
    - If some info or entity in the user's question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    - Assume that some of the properties might not appear in data we are querying, keep the the number of attributes you include as low as possible
    - If you see some $ref values with links, resolve them if needed to answer the user's question
    
    Generate the SPARQL query to answer the user's question.
    Be as concise as possible.
    
    Question: \n
    {user_question}
    \n
    
    Publisher names: \n	
    {publishers}
    \n
    
    Names of the datasets: \n
    {titles}
    \n
    
    Schemas:\n
    {schemas}
    \n
    """
}


nkod_entities_system = {
    "gpt-5":"""
    
    """
}


nkod_graph_sparq_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.
    Given one or more schemas and a natural language query, generate a valid SPARQL query.
    """
}


nkod_graph_sparql_user = {
    "gpt-5": """
    Task
    Generate a SPARQL SELECT statement for querying a graph database.
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation. 
    Use only classes and properties defined the schema(s).
    If some info in the user question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    Your task is to generate correct, efficient, and human-readable SPARQL query given:
        (1) metadata, and 
        (2) a natural language question.
    
    Example
    For instance, to find all email addresses of John Doe, the following query in backticks would be suitable:
    ```
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?email
    WHERE {{
        ?person foaf:name "John Doe" .
        ?person foaf:mbox ?email .
    }}
    ```
    Instructions:
    - Use only the node types and properties provided.
    - Do not use EXISTS {{}} clauses.
    - Do not use any node types and properties that are not explicitly provided.
    - Include all necessary prefixes.
    - Note: Be as concise as possible.
    - Do not include any explanations or apologies in your responses.
    - Do not respond to any questions that ask for anything else than for you to construct a SPARQL query.
    - Do not include any text except the SPARQL query generated.
    - Use only classes and properties defined the metadata below.
    - There might be multiple metadata from multiple datasets, handle them appropriately and connect them using common properties.
    - If some info or entity in the user's question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    
    Generate the SPARQL query to answer the user's question. 
    Be as concise as possible.
    
    Node types (In the following, each IRI is followed by the local name and optionally its description in parentheses): \n
    {classes}
    \n
    
    Relationships (In the following, each IRI is followed by the local name and optionally its description in parentheses): \n
    {relationships}
    \n
    
    Publisher names: \n	
    {publishers}
    \n
    
    Names of the datasets: \n
    {titles}
    \n
    
    Question: \n
    {question}
    \n
    """
}


nkod_openai_files_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.
    Given one or more RDF files and a natural language query, generate a valid SPARQL query.
    """
}


nkod_openai_files_user = {
    "gpt-5": """
    Task
    Generate a SPARQL SELECT statement for querying a graph database.
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation. 
    Use only classes and properties defined the attached files.
    If some info in the user question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    Your task is to generate correct, efficient, and human-readable SPARQL query given:
        (1) attached files, and 
        (2) a natural language question.
    
    Example
    For instance, to find all email addresses of John Doe, the following query in backticks would be suitable:
    ```
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?email
    WHERE {{
        ?person foaf:name "John Doe" .
        ?person foaf:mbox ?email .
    }}
    ```
    Instructions:
    - Use only the node types and properties provided.
    - Do not use EXISTS {{}} clauses.
    - Do not use any node types and properties that are not explicitly provided.
    - Include all necessary prefixes.
    - Note: Be as concise as possible.
    - Do not include any explanations or apologies in your responses.
    - Do not respond to any questions that ask for anything else than for you to construct a SPARQL query.
    - Do not include any text except the SPARQL query generated.
    - Use only classes and properties defined the attached files.
    - There might be multiple attached files from multiple datasets, handle them appropriately and connect them using common properties.
    - If some info or entity in the user's question are already included in the publisher name or name of the dataset, 
    do not include them in the SPARQL query
    
    Generate the SPARQL query to answer the user's question. 
    Be as concise as possible.

    Publisher names: \n	
    {publishers}
    \n
    
    Names of the datasets: \n
    {titles}
    \n
    
    Question: \n
    {question}
    \n
    """
}






