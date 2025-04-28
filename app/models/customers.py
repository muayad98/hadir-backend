from datetime import datetime
from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string")

class CustomerBase(BaseModel):
    whatsapp_id: str = Field(..., description="Twilio's unique conversation ID")
    phone: str = Field(..., description="E.164 format phone number")
    name: Optional[str] = Field(None, description="Customer's name")
    language: Literal["ar", "en"] = Field(..., description="Preferred language")

class CustomerCreate(CustomerBase):
    pass

class CustomerInDB(CustomerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CustomerResponse(CustomerInDB):
    id: str = Field(alias="_id")

    class Config:
        validate_by_name = True
        json_encoders = {ObjectId: str} 