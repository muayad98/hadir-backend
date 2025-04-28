from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field, validator
from bson import ObjectId

from app.models.base import PyObjectId

class Message(BaseModel):
    dir: Literal["in", "out"]
    text: str
    ts: datetime

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('text must not be empty')
        return v.strip()

    @validator('ts')
    def validate_datetime(cls, v):
        if not isinstance(v, datetime):
            raise ValueError('ts must be a valid datetime')
        return v

class ConversationBase(BaseModel):
    business_id: PyObjectId
    customer_id: PyObjectId

class ConversationInDB(ConversationBase):
    id: PyObjectId = Field(default_factory=PyObjectId)
    messages: List[Message] = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class ConversationResponse(ConversationInDB):
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True 