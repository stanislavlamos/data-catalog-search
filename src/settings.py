class Settings:
    def __init__(self):
        self._model_provider = None
        self._embedding_provider = None
        self._llm_type = None
        self._embedding_type = None
        self._data_processor = None
        self._query_matcher = None
        self._user_query = None

    def update_settings_from_request(self):
        pass




