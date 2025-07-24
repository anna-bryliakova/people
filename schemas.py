from typing import Optional
from pydantic import BaseModel, Field


class CreatePerson(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., min_length=1, max_length=150)
    mother_id: Optional[int] = Field(default=None, examples=[None])
    father_id: Optional[int] = Field(default=None, examples=[None])
