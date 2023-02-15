from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    date_created:  datetime = Field(default=datetime.now())
    transactions: int = Field(default=0)


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
