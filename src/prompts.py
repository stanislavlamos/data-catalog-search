# You are a language classifier. Classify any text as Czech, English, or Other. If the text contains a mixture of Czech and English, or any other language, classify it as Other
language_detection_system = {
    "gpt-5": "Classify the given text as 'Czech', 'English', or 'Other'. If the text contains a mix of Czech and English, or any language other than Czech or English, classify it as 'Other'.",
    "gpt-4.1": "Classify the input text as one of the following: Czech, English, or Other. If the text is a mixture of Czech, English, or any other languages, classify it as Other.",
    "gpt-3o": "Classify the input text as 'Czech', 'English', or 'Other'. If the text contains a mix of languages, select 'Other'. Return your answer as a single word."
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