from pydantic import BaseModel
from typing import List


class TextRequest(BaseModel):
    text: str


class InsightResult(BaseModel):
    summary: str
    action_items: List[str]
    key_decisions: List[str]
    prompt_tokens: int
    completion_tokens: int