from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    date_created:  datetime = Field(default=datetime.now())
    verification_id: int


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
