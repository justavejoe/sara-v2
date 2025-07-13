from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class ResearchPaper(BaseModel):
    id: int
    title: str
    authors: List[str]
    publication_date: Optional[date] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    content: str
    embedding: List[float]
    source_url: Optional[str] = None
    keywords: List[str] = []