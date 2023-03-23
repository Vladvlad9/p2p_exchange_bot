from pydantic import BaseModel, Field


class OperationSchema(BaseModel):
    name: str


class OperationInDBSchema(OperationSchema):
    id: int = Field(ge=1)
