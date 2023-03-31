from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    date_created:  datetime = Field(default=datetime.now())
    verification_id: int = Field(default=0)
    transaction_timer: bool = Field(default=False)


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
