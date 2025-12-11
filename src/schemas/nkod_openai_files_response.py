from pydantic import BaseModel


class NkodOpenAiFilesResponse(BaseModel):
    sparql_query: str
    query_result: dict | list
    is_executable: bool = True
    summary: str = ""
