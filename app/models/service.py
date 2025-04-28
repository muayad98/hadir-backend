from typing import Optional
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from bson import ObjectId
from pydantic_core import CoreSchema, core_schema
from typing import Any

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

class ServiceBase(BaseModel):
    business_id: PyObjectId
    name_en: str = Field(..., min_length=1)
    name_ar: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., ge=5, le=300)
    price: Optional[float] = Field(None, ge=0)
    active: bool = Field(default=True)

    model_config = {
        "json_encoders": {ObjectId: str}
    }

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name_en: str = Field(None, min_length=1)
    name_ar: str = Field(None, min_length=1)
    duration_minutes: Optional[int] = Field(None, ge=5, le=300)
    price: Optional[float] = Field(None, ge=0)
    active: Optional[bool] = None

    model_config = {
        "json_encoders": {ObjectId: str}
    }

class ServiceInDB(ServiceBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "validate_assignment": True
    }

class ServiceResponse(ServiceBase):
    id: str

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    } 