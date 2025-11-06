from pydantic import BaseModel


class NkodOpenAiFilesResponse(BaseModel):
    sparql_query: str
    query_result: list
    is_executable: bool = True
    summary: str = ""
