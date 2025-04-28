from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator, GetJsonSchemaHandler
from datetime import time
import pytz
from bson import ObjectId
from pydantic_core import CoreSchema, core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetJsonSchemaHandler,
    ) -> CoreSchema:
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
        raise ValueError('Invalid ObjectId')

class WorkingHours(BaseModel):
    day: int = Field(..., ge=0, le=6)
    start: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")

    @validator('end')
    def end_must_be_after_start(cls, v, values):
        if 'start' in values:
            start_time = time.fromisoformat(values['start'])
            end_time = time.fromisoformat(v)
            if end_time <= start_time:
                raise ValueError('end time must be after start time')
        return v

class BusinessBase(BaseModel):
    name: str
    whatsapp_number: str = Field(..., pattern="^\+[1-9]\d{1,14}$")  # E.164 format
    timezone: str
    working_hours: List[WorkingHours]
    accepting_bookings: bool = True
    buffer_minutes: int = Field(..., ge=0, le=120)
    language_default: str = Field(..., pattern="^(ar|en)$")

    @validator('timezone')
    def validate_timezone(cls, v):
        try:
            pytz.timezone(v)
            return v
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError('Invalid timezone')

    model_config = {
        "json_encoders": {ObjectId: str}
    }

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BusinessBase):
    pass

class BusinessInDB(BusinessBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "validate_assignment": True
    }

class BusinessResponse(BusinessBase):
    id: str

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    } 