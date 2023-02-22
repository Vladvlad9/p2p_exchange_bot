from datetime import datetime
from pydantic import BaseModel, Field


class CurrencySchema(BaseModel):
    name: str


class CurrencyInDBSchema(CurrencySchema):
    id: int = Field(ge=1)
