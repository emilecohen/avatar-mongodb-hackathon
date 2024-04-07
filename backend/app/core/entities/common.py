from typing import List
from pydantic.main import BaseModel


class IndexWebsiteInput(BaseModel):
    urls: List[str]
    company_name: str


class GetAnswerInput(BaseModel):
    company_name: str
    query: str


class GetAnswerOutput(BaseModel):
    response: str
