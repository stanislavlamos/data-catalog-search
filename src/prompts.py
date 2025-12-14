language_detection_system = {
    "gpt-5": "You are a helpful assistant, classify the given text as 'Czech', 'English', or 'Other'. If the text contains a mix of Czech and English, or any language other than Czech or English, classify it as 'Other'. Do not take entities and concrete names into account, such as: cities, names, places, food etc...",
    "gpt-4.1-nano": """
    You are a helpful assistant. Your task is to classify the input text as one of the following: Czech, English, or Other.  

    - If the text is a mixture of Czech, English, or any other languages, classify it as Other.  
    - Ignore specific entities such as cities, personal names, places, foods, or other proper nouns—they should not affect the classification.
    """
}


language_detection_user = {
    "gpt-4.1-nano": """
    You are a language classifier. Classify the language of the given text into one of three categories: "english", "czech", or "other". Use the following examples as guidance:

    Examples:
    - "Hello" → english
    - "Ahoj" → czech
    - "Jaké události v Říčanech se týkají hudby?" → czech
    - "Official bulletin board Ostrava - Trebovice" → english
    - "Official bulletin board Rožnov pod Radhoštěm" → english
    - "ZPS obec Studenec" → czech
    - "Hello, ahoj" → other
    - "Bonjour" → other
    
    Now classify the following text:
    
    {text}
    """
}


timeframe_detection_system = {
    "gpt-4.1": """
    Role: Build a helpful assistant to extract explicit timeframes from user queries.

    Instructions:
      - Scan the user's query for explicit timeframes (e.g., "next week", "last month").
      - Interpret relative phrases using today’s date: {today}.
      - Convert any identified timeframe into start and end dates in ISO 8601 format (YYYY-MM-DD).
      - If the timeframe is ambiguous or incomplete (e.g., "June" without a year), set both dates to null and indicate that no valid timeframe was found.
      - Always output a valid JSON object using the schema below.
      - Validate your output and self-correct to ensure the JSON is correct and dates are consistent.
    
    JSON Output Schema:
    {{
      "timeframe": true | false,
      "start_date": "YYYY-MM-DD" | null,
      "end_date": "YYYY-MM-DD" | null
    }}
    
    Notes:
      - Always output strictly in the JSON format above.
      - Use the system's current time zone ({today}) for all calculations.
      - Refine your response until it either produces a valid timeframe or explicitly indicates no timeframe.
    """
}


timeframe_detection_user = {
    "gpt-4.1": """
    Role: Extract explicit timeframes from a user query.
    Instructions:
      - Analyze the user's query: {user_query}.
      - Look for explicit timeframes (e.g., "next week", "last month").
      - Interpret relative phrases using today’s date: {today}.
      - Convert any identified timeframe to start and end dates in ISO 8601 format (YYYY-MM-DD).
      - If the timeframe is ambiguous or incomplete (e.g., "June" without a year), set both dates to null and indicate no valid timeframe.
      - Always output valid JSON using the schema below.
      - Validate and self-correct the output to ensure correctness.
    
    JSON Output Schema:
    {{
      "timeframe": true | false,
      "start_date": "YYYY-MM-DD" | null,
      "end_date": "YYYY-MM-DD" | null
    }}
    
    Examples:
    
    1. User Query: "Ukaž data za minulý týden"
       JSON Output:
       {{
         "timeframe": true,
         "start_date": "2025-12-16",
         "end_date": "2025-12-22"
       }}
    
    2. User Query: "Chci vidět data za minulý měsíc"
       JSON Output:
       {{
         "timeframe": true,
         "start_date": "2025-11-01",
         "end_date": "2025-11-30"
       }}
    
    3. User Query: "Ukaž data za červen 2025"
       JSON Output:
       {{
         "timeframe": true,
         "start_date": "2025-06-01",
         "end_date": "2025-06-30"
       }}
    
    Notes:
      - Output strictly in the JSON format above.
      - Use the system's current time zone ({today}) for all calculations.
    """
}


nkod_query_matching_dataset_simple_system = {
    "gpt-4.1": """
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
    "gpt-4.1": """
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
    "gpt-4.1": """
    You are an advanced dataset recommender.
    You will be given a user query and a list of candidate datasets (Doc + URI).
    Your task is to rerank all the datasets based on how they reflect the user query.
    Consider relevance, coverage, and complementarity of the Doc field to the query from the user.
    Rank the selected datasets from most relevant to least relevant.
    Return in the provided structured format.
    Always return all the datasets you received on the input
    Do not change the URIs or Docs.
    """,
    "gpt-5": """
    You are an advanced dataset recommender.
    You will receive a user query and a list of candidate datasets (each with Doc + URI).
    Rerank all datasets by how well their Doc content aligns with the query—consider relevance, coverage, specificity, and complementarity.
    Return every dataset in the required structured format, ordered from most to least relevant.
    Do not alter any Docs or URIs.
    """
}


nkod_query_matching_llm_judge_user = {
    "gpt-4.1": """
    You are given a user query describing the datasets they need, and a list of candidate datasets with Doc and URIs.
    
    Your task is to rerank the datasets based on how they satisfy the user's query.
    - Consider relevance, coverage, and complementarity.
    - Rank all input datasets from most relevant to least relevant.
    - Assign a relevance_score between 0 (irrelevant) and 1 (perfectly relevant).
    - Use the Doc field for the reranking with respect to user's query.
    - Always return all the datasets you received on the input.
    
    Return the output in the provided structured format.
    Return all {n_datasets} datasets you received on the input.

    User Query:
    {user_query}
    
    Candidate Datasets:
    {datasets}
    """,
    "gpt-5": """
    You are given:
    - A user query describing the datasets they need.
    - A list of candidate datasets, each with a Doc field and a URI.
    
    Task:
    Rerank all candidate datasets based on how well they satisfy the user’s query.
    
    Reranking Criteria:
    1. Relevance – How directly the dataset addresses the user’s query.
    2. Coverage – How fully the dataset covers the requested information.
    3. Complementarity – How useful the dataset is in combination with others, relative to the query.
    
    Instructions:
    - Rank all provided datasets from most relevant to least relevant.
    - For each dataset, assign a relevance_score in the range [0, 1], where:
      - 1 = perfectly relevant
      - 0 = irrelevant
    - Use only the Doc field to assess relevance to the user’s query.
    - Always return all {n_datasets} datasets in the output.
    - Follow the provided structured output format.
    
    User Query:
    {user_query}
    
    Candidate Datasets:
    {datasets}
    """
}


nkod_rag_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.

    Your task is to generate a correct, efficient, and semantically accurate SPARQL query using:
    - One or more schemas provided in JSON, JSON-LD, Turtle (.ttl), XML, RDF/XML, or TriG (.trig) formats.
    - A natural language question.
    
    Interpret all schemas precisely, respect prefixes and namespaces, and use only classes and properties defined in the provided schema(s).
    """
}


nkod_rag_user = {
    "gpt-5": """
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation.
    
    Your task is to generate a correct, efficient, and human-readable SPARQL query using:
    1. One or more schemas provided in RDF, JSON, XML, JSON-LD, Turtle (.ttl), or TriG (.trig) format.
    2. A natural language question.
    
    ### INSTRUCTIONS
    
    SCHEMA CONSTRAINTS:
    - Use only classes and properties defined in the provided schema(s).
    - Correctly interpret prefixes and namespaces.
    - If any info in the user's question is already implied by the publisher names or dataset titles, do NOT include it in the query.
    - Do not make assumptions beyond what appears in the schema(s).
    - If `$ref` values reference external definitions, resolve them only if needed.
    
    QUERY CONSTRAINTS:
    - Produce a syntactically valid and semantically consistent SPARQL query.
    - Do NOT use `EXISTS {{}}` clauses.
    - Keep the query concise; include only triples strictly needed to answer the question.
    - Assume some properties may not appear in the data; keep attribute usage minimal.
    - Do NOT output comments or explanations.
    - Output ONLY a SPARQL query inside a fenced code block: ```sparql ... ```
    - The query must be efficient and avoid unnecessary complexity.
    - Respect the language used in the schemas; do NOT translate labels, IRIs, or literals.
    
    MULTI-SCHEMA HANDLING:
    - Multiple schemas may be provided.
    - Connect schemas only where explicit links (shared URIs, shared classes, or shared properties) exist.
    
    ### FEW-SHOT EXAMPLES
    
    {few_shot_queries}
    
    ### INPUTS
    
    Question:
    {user_question}
    
    Publisher names:
    {publishers}
    
    Dataset titles:
    {titles}
    
    Schemas:
    {schemas}
    
    ### FINAL TASK
    
    Generate the SPARQL query that answers the user's question.
    Return ONLY the SPARQL query in a fenced code block labeled `sparql` in this format:
     ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}


nkod_rag_error_user = {
    "gpt-5": """
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation.
    
    Your task is to generate a correct, efficient, and human-readable SPARQL query using:
    1. One or more schemas provided in RDF, JSON, XML, JSON-LD, Turtle (.ttl), or TriG (.trig) format.
    2. A natural language question.
    
    ### ERROR LOOP / SELF-CORRECTION MODE
    
    A previously generated SPARQL query has failed.
    
    # Failing Query and Error
    **Failing SPARQL query:**  
    {failing_query}
    
    **Stacktrace / Error Message:**  
    {stack_trace}
    
    When a failing query and its error message are provided:
    - Enter **self-correction mode**.
    - Re-evaluate the schema(s), the question, the failing query, and the error message.
    - Infer the cause of the failure internally.
    - Regenerate a corrected version of the query that resolves the issue completely.
    - Do NOT repeat structural, syntactic, or semantic mistakes from earlier attempts.
    - Do NOT output explanations, analysis, or commentary.
    - Output only the corrected SPARQL query.
    
    ### INSTRUCTIONS
    
    SCHEMA CONSTRAINTS:
    - Use only classes and properties defined in the provided schema(s).
    - Correctly interpret prefixes and namespaces.
    - If any info in the user's question is already implied by the publisher names or dataset titles, do NOT include it in the query.
    - Do not make assumptions beyond what appears in the schema(s).
    - If `$ref` values reference external definitions, resolve them only if needed.
    
    QUERY CONSTRAINTS:
    - Produce a syntactically valid and semantically consistent SPARQL query.
    - Do NOT use `EXISTS {{}}` clauses.
    - Keep the query concise; include only triples strictly needed to answer the question.
    - Assume some properties may not appear in the data; keep attribute usage minimal.
    - Do NOT output comments or explanations.
    - Output ONLY a SPARQL query inside a fenced code block: ```sparql ... ```
    - The query must be efficient and avoid unnecessary complexity.
    - Respect the language used in the schemas; do NOT translate labels, IRIs, or literals.
    
    MULTI-SCHEMA HANDLING:
    - Multiple schemas may be provided.
    - Connect schemas only where explicit links (shared URIs, shared classes, or shared properties) exist.
    
    ### FEW-SHOT EXAMPLES
    
    {few_shot_queries}
    
    ### INPUTS
    
    Question:
    {user_question}
    
    Publisher names:
    {publishers}
    
    Dataset titles:
    {titles}
    
    Schemas:
    {schemas}
    
    ### FINAL TASK
    
    Generate a fully corrected SPARQL query that answers the user's question.
    Return ONLY the SPARQL query in a fenced code block labeled `sparql` in this format:
     ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}


nkod_graph_sparq_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.

    Input: A set of classes (with descriptions), relationships (with descriptions), publisher names, dataset titles, and a natural language query.
    
    Output: SPARQL SELECT query only, in a markdown code block with `sparql` as the identifier. Do not include any extra content.
    
    Guidelines:
    - Query must be syntactically valid and follow RDF standards.
    - Use only the provided classes and relationships.
    - Include all necessary PREFIX declarations.
    - Omit any information already implied by publisher names or dataset titles.
    - When multiple datasets are provided, connect them using shared properties.
    - Do not include explanations, metadata, comments, or extra text.
    - Stop after generating the first valid query.
    - Be concise, efficient, and human-readable.
    
    Output: 
    Return only the SPARQL SELECT query as plain text. Do not include explanations, comments, or any content outside of the query. Use only the supplied classes and properties.
    """
}


nkod_graph_sparql_user = {
    "gpt-5": """
    # Task
    Generate a correct, efficient, and human-readable **SPARQL SELECT** query for querying a graph database.  
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation.  
    
    Use only the **classes and properties defined in the provided metadata**, including their descriptions.  
    If information in the user question is already implied by the **publisher names** or **dataset titles**, do **not** include it in the SPARQL query.
    
    # Instructions
    - Use only the provided node types and properties.  
    - Do **not** use `EXISTS {{}}` clauses.  
    - Include all necessary PREFIX declarations.  
    - Be as concise as possible.  
    - Do **not** include explanations, commentary, or any text outside the SPARQL query.  
    - Handle multiple datasets by connecting them using shared properties.  
    - Respond **only** with the SPARQL query.  
    
    # Few-Shot Examples
    {few_shot_queries}
    
    # Metadata
    
    **Classes (with descriptions):**  
    {classes}  
    *(Each IRI is followed by the local name and optionally a description in parentheses)*
    
    **Relationships (with descriptions):**  
    {relationships}  
    *(Each IRI is followed by the local name and optionally a description in parentheses)*
    
    **Publisher names:**  
    {publishers}
    
    **Dataset titles:**  
    {titles}
    
    **User Question:**  
    {user_question}
    
    # Output
    Return a single **SPARQL SELECT** query that answers the user's question in this format:
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}


nkod_graph_sparql_error_user = {
    "gpt-5": """
    # Task
    A previously generated SPARQL query failed to execute.  
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL query generation.  
    Your goal is to generate a **correct, executable, efficient, and human-readable SPARQL SELECT query** that answers the user's question.
    
    # Metadata
    **Classes (with descriptions):**  
    {classes}
    
    **Relationships (with descriptions):**  
    {relationships}
    
    **Publisher names:**  
    {publishers}
    
    **Dataset titles:**  
    {titles}
    
    **User Question:**  
    {user_question}
    
    # Failing Query and Error
    **Failing SPARQL query:**  
    {failing_query}
    
    **Stacktrace / Error Message:**  
    {stack_trace}
    
    # Rules / Instructions
    - Use only the provided node types and properties.  
    - Do **not** add information implied by the publisher names or dataset titles.  
    - Do **not** use `EXISTS {{}}` clauses.  
    - Include all necessary PREFIX declarations.  
    - Be as concise as possible.  
    - Handle multiple datasets by connecting them through shared properties.  
    - Respond **only** with the SPARQL query.  
    - Do **not** include explanations, commentary, or any text outside the SPARQL query.  
    
    # Output Format
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    """
}


nkod_openai_files_system = {
    "gpt-5": """
    You are an expert in RDF, OWL, and SPARQL.    
    Generate a correct, concise, and human-readable SPARQL SELECT query using only the classes and properties specified in the provided input. Be sure to include all necessary PREFIX declarations.
    
    Guidelines:
    - Do not use undefined classes or properties.
    - Do not include EXISTS {{}} constructs, explanations, or any additional text beyond the required query.
    - Omit information that is already implied by publisher names or dataset titles.
    - If handling multiple datasets, use shared properties to relate their data.
    - Respond solely with the SPARQL query.
    
    After constructing the query, perform a brief validation to ensure all used classes and properties match those provided and that all required PREFIX declarations are present.
    
    ## Output Format
    Return only the completed SPARQL SELECT query as plain text. Do not include explanations, comments, or any content outside of the query. Use only the supplied classes and properties.
    """,
    "gpt-4.1": """
    You are an expert in RDF, OWL, and SPARQL.  
    Generate a correct, concise, human-readable **SPARQL SELECT** query using only the classes and properties provided. Include all required **PREFIX** declarations.
    
    - Use only the supplied classes and properties.  
    - Do not include `EXISTS {{}}`, explanations, or extra text.  
    - Omit info already implied by publisher names or dataset titles.  
    - For multiple datasets, connect them via shared properties.  
    - Ensure all classes/properties exist in the input and all PREFIXes are included.  
    
    **Output:**  
    Return only the SPARQL SELECT query as plain text. Do not include explanations, comments, or any content outside of the query. Use only the supplied classes and properties.
    """
}


nkod_openai_files_user = {
    "gpt-5": """
    # Task
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL.  
    Generate a correct, efficient, and human-readable **SPARQL SELECT** query using:
    1. The classes and properties defined in the **attached OpenAI files**, and  
    2. The user's natural-language question.
    
    # Requirements
    - Use **only** the classes and properties defined in the attached files.
    - Include **all required PREFIX** declarations.
    - The query must be **concise**, with no unnecessary patterns.
    - **Do NOT** use:
      - `EXISTS {{ }}`
      - Any undefined classes or properties
      - Any explanations, commentary, or apologies
      - Any output other than the SPARQL query itself
    - If multiple datasets are included, connect them only using **explicitly shared properties**.
    - If the user question contains information already implied by:
      - The **publisher names**, or
      - The **dataset titles**,  
      then **do not duplicate** that information in the SPARQL query.
    
    ---
    
    # Few-Shot Examples\n
    {few_shot_queries}
    
    ---
    
    # Inputs
    
    **Publisher names:**  
    ```
    {publishers}
    ```
    
    **Dataset titles:**  
    ```
    {titles}
    ```
    
    **User Question:**  
    ```
    {user_question}
    ```
    
    ---
    
    # Output
    A single **SPARQL SELECT** query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
    …
    }}
    ```
    """,
    "gpt-4.1": """
    # Task
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL.  
    Generate a correct, efficient, and human-readable **SPARQL SELECT** query using:  
    1. Classes and properties defined in the **attached OpenAI files**  
    2. The user's natural-language question
    
    # Requirements
    - Use **only** the classes and properties defined in the attached files.
    - Include **all required PREFIX** declarations.
    - The query must be **concise**, with no unnecessary patterns.
    - **Do NOT** use:
      - `EXISTS {{ }}`
      - Any undefined classes or properties
      - Explanations, commentary, or apologies
      - Any output other than the SPARQL query
    - When multiple datasets are included, connect them only via **explicitly shared properties**.
    - If the user question contains info already implied by:
      - The **publisher names**, or
      - The **dataset titles**,  
      then **omit it** in the SPARQL query.
    
    ---
    
    # Few-Shot Examples
    {few_shot_queries}
    
    ---
    
    # Inputs
    
    **Publisher names:**  
    ```
    {publishers}
    ```
    
    **Dataset titles:**  
    ```
    {titles}
    ```
    
    **User Question:**  
    ```
    {user_question}
    ```
    
    ---
    
    # Output
    Return **only** a single **SPARQL SELECT** query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}


nkod_openai_files_error_user = {
    "gpt-5": """
    # Task
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL.  
    You are given a **previous SPARQL query** that produced an error, along with its **stacktrace**.  
    Your task is to **correct the query** so that it is executable, efficient, and human-readable, using:  
    1. Classes and properties defined in the **attached OpenAI files**, and  
    2. The user's natural-language question.
    
    # Requirements
    - Use **only** the classes and properties defined in the attached files.
    - Include **all required PREFIX** declarations.
    - The corrected query must be **concise** and fully executable.
    - **Do NOT** use:
      - `EXISTS {{ }}`
      - Any undefined classes or properties
      - Optional or unresolvable patterns that would break execution
      - Explanations, commentary, or apologies
      - Any output other than the corrected SPARQL query
    - If multiple datasets are included, connect them only via **explicitly shared properties**.
    - If the user question contains info already implied by:
      - The **publisher names**, or
      - The **dataset titles**,  
      then **omit it** in the query.
    - Validate that every variable and triple resolves with the attached classes/properties.
    
    ---
    
    # Few-Shot Examples
    {few_shot_queries}
    
    ---
    
    # Inputs
    
    **Publisher names:**  
    ```
    {publishers}
    ```
    
    **Dataset titles:**  
    ```
    {titles}
    ```
    
    **User Question:**  
    ```
    {user_question}
    ```
    
    **Previous Query:**  
    ```
    {failing_query}
    ```
    
    **Stacktrace:**  
    ```
    {stack_trace}
    ```
    
    ---
    
    # Output
    Return **only** a single **corrected SPARQL SELECT** query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """,
    "gpt-4.1": """
    # Task
    You are an expert in Semantic Web technologies, RDF, OWL ontologies, and SPARQL.  
    You are given a **previous SPARQL query** that failed, along with its **stacktrace**.  
    Your task is to **correct the query** so it is executable, efficient, and human-readable, using:  
    1. Classes and properties defined in the **attached OpenAI files**, and  
    2. The user's natural-language question.
    
    # Requirements
    - Use **only** the classes and properties defined in the attached files.
    - Include **all required PREFIX** declarations.
    - The corrected query must be **concise** and fully executable.
    - **Do NOT** use:
      - `EXISTS {{ }}`
      - Any undefined classes or properties
      - Optional or unresolvable patterns that would break execution
      - Explanations, commentary, or apologies
      - Any output other than the corrected SPARQL query
    - When multiple datasets are included, connect them only via **explicitly shared properties**.
    - If the user question contains info already implied by:
      - The **publisher names**, or
      - The **dataset titles**,  
      then **omit it** in the query.
    - Ensure that every variable and triple resolves with the attached classes/properties.
    
    ---
    
    # Few-Shot Examples
    {few_shot_queries}
    
    ---
    
    # Inputs
    
    **Publisher names:**  
    ```
    {publishers}
    ```
    
    **Dataset titles:**  
    ```
    {titles}
    ```
    
    **User Question:**  
    ```
    {user_question}
    ```
    
    **Previous Query:**  
    ```
    {failing_query}
    ```
    
    **Stacktrace:**  
    ```
    {stack_trace}
    ```
    
    ---
    
    # Output
    Return **only** a single **corrected SPARQL SELECT** query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}


nkod_shacl_system = {
    "gpt-5": """
    You are an expert in RDF, SPARQL query generation, and ontology modeling.
    
    Input: SHACL schemas (Turtle) and a natural language query.
    
    Output: SPARQL query only, in a markdown code block with 'sparql' as the identifier. No extra content.
    
    - Query must be syntactically valid and follow RDF standards.
    - Use only properties/classes from provided schemas.
    - Encode any relevant SHACL constraints.
    - Do not include explanation, metadata, or comments.
    - Stop after the first valid query.
    """
}

nkod_shacl_user = {
    "gpt-5": """
    You are an expert in Semantic Web technologies, RDF, OWL, SHACL, and SPARQL query generation.
    
    Your task is to generate a correct, efficient SPARQL query given:
    1. A set of SHACL schemas
    2. A natural-language question
    
    Follow these strict rules:
    - Use ONLY classes and properties defined in the provided schema(s).
    - Parse prefixes and namespaces exactly as defined.
    - Do NOT invent classes or properties.
    - Do NOT use EXISTS {{}}.
    - Keep the query minimal and efficient.
    - If information in the question is already implied by publisher names or dataset titles, do NOT repeat it in the SPARQL query.
    - Do NOT add assumptions not supported by the schemas.
    - Output ONLY the SPARQL query inside a fenced ```sparql code block.
    - No explanations or comments of any kind.
    
    ---
    
    ## FEW-SHOT EXAMPLES \n
    {few_shot_queries}
    
    ---
    
    ## NOW GENERATE THE QUERY
    
    **Question:**  
    {user_question}
    
    **Publisher names:**  
    {publishers}
    
    **Dataset titles:**  
    {titles}
    
    **Schemas:**\n 
    {schemas}
    
    ---
    
    ## OUTPUT FORMAT
    Return ONLY a valid SPARQL query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
    …
    }}
    ```
    """
}


nkod_shacl_error_user = {
    "gpt-5": """
    You are an expert in Semantic Web technologies, RDF, OWL, SHACL, and SPARQL query generation.
    
    A previously generated SPARQL query produced an error.  
    Your task is to produce a **corrected, valid, and efficient** SPARQL query using:
    1. The same natural-language question  
    2. The provided schemas  
    3. The failing SPARQL query  
    4. The stack trace  
    5. The same strict constraints below  
    
    Follow these rules:
    - Use ONLY classes and properties defined in the provided schema(s).
    - Parse and respect prefixes and namespaces exactly as defined.
    - Do NOT invent any classes, properties, or prefixes.
    - Do NOT use EXISTS {{}}.
    - Keep the query minimal and efficient.
    - Fix ALL errors indicated by the stack trace or error message.
    - Do NOT add assumptions not supported by the schemas.
    - If information in the question is already implied by publisher names or dataset titles, do NOT repeat it in the SPARQL query.
    - Output ONLY a corrected SPARQL query inside a fenced ```sparql code block.
    - Do NOT output explanations or comments.
    
    ---
    
    ## FEW-SHOT EXAMPLES \n
    {few_shot_queries}
    
    ---
    
    ## NOW FIX THE QUERY
    
    **Original Question:**  
    {user_question}
    
    **Publisher names:**  
    {publishers}
    
    **Dataset titles:**  
    {titles}
    
    **Schemas:** \n 
    {schemas}
        
    ---
    
    ## Failing SPARQL Query
    ```sparql
    {failing_query}
    ```
    
    ---
    
    ## Stack Trace
    {stack_trace}
    
    ---
    
    ## OUTPUT FORMAT
    Return ONLY a corrected SPARQL query in this format:
    
    ```sparql
    SELECT …
    WHERE {{
      …
    }}
    ```
    """
}
