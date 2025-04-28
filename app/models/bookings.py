from typing import Optional, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_core import CoreSchema, core_schema
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: CoreSchema) -> CoreSchema:
        return core_schema.union_schema([
            core_schema.str_schema(),
            core_schema.is_instance_schema(ObjectId),
        ])

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")

class BookingBase(BaseModel):
    business_id: PyObjectId
    customer_id: PyObjectId
    service_id: PyObjectId
    start_time: datetime  # UTC, timezone-aware

    model_config = {"json_encoders": {ObjectId: str}}

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Literal["confirmed", "cancelled", "rescheduled", "completed", "no_show"]

    model_config = {"json_encoders": {ObjectId: str}}

class BookingInDB(BookingBase):
    id: PyObjectId = Field(alias="_id")
    end_time: datetime
    status: str
    created_via: Literal["ai", "admin"]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }

class BookingResponse(BookingInDB):
    id: str

    model_config = {"populate_by_name": True, "validate_assignment": True} 