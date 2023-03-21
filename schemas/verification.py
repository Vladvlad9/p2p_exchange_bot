from pydantic import BaseModel, Field


class VerificationSchema(BaseModel):
    user_id: int = Field(ge=1)
    photo_id: list[str]
    confirm: bool = False


class VerificationInDBSchema(VerificationSchema):
    id: int = Field(ge=1)
