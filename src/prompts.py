# You are a language classifier. Classify any text as Czech, English, or Other. If the text contains a mixture of Czech and English, or any other language, classify it as Other
language_detection_system = {
    "gpt-5": "You are a helpful assistant, classify the given text as 'Czech', 'English', or 'Other'. If the text contains a mix of Czech and English, or any language other than Czech or English, classify it as 'Other'.",
    "gpt-4.1": "You are a helpful assistant, classify the input text as one of the following: Czech, English, or Other. If the text is a mixture of Czech, English, or any other languages, classify it as Other.",
    "gpt-3o": "You are a helpful assistant, classify the input text as 'Czech', 'English', or 'Other'. If the text contains a mix of languages, select 'Other'. Return your answer as a single word."
}

language_detection_user = {
    "gpt-5": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text:
        {text}
    """,

    "gpt-4.1": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text:
        {text}
    """,

    "gpt-3o": """
        Here are some examples:
        "Hello" → english
        "Ahoj" → czech
        "Hello, ahoj" → other
        "Bonjour" → other
    
        Classify the following text:
        {text}
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
