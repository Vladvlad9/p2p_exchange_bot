from pydantic import BaseModel, Field


class ReferralSchema(BaseModel):
    user_id: int = Field(ge=1)
    referral_id: int


class ReferralInDBSchema(ReferralSchema):
    id: int = Field(ge=1)
