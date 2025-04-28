from fastapi import APIRouter, HTTPException
from typing import List
from app.models.service import ServiceCreate, ServiceResponse, ServiceInDB, ServiceUpdate
from app.db import db
from bson import ObjectId
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ServiceResponse)
async def create_service(service: ServiceCreate):
    try:
        # Convert Pydantic model to dict
        service_dict = service.model_dump()
        
        # Verify business exists
        business = await db.get_collection("businesses").find_one({"_id": ObjectId(service_dict["business_id"])})
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Insert service
        result = await db.get_collection("services").insert_one(service_dict)
        
        # Get the inserted document
        inserted_service = await db.get_collection("services").find_one({"_id": result.inserted_id})
        
        # Convert _id to string for response
        inserted_service["id"] = str(inserted_service.pop("_id"))
        return ServiceResponse(**inserted_service)
        
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ServiceResponse])
async def get_services(business_id: str):
    try:
        # Verify business exists
        business = await db.get_collection("businesses").find_one({"_id": ObjectId(business_id)})
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        services = []
        async for service in db.get_collection("services").find({"business_id": business_id}):
            # Convert _id to string for response
            service["id"] = str(service.pop("_id"))
            services.append(ServiceResponse(**service))
        return services
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_update: ServiceUpdate):
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in service_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")
            
        # Update service
        result = await db.get_collection("services").update_one(
            {"_id": ObjectId(service_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
            
        # Get updated service
        updated_service = await db.get_collection("services").find_one({"_id": ObjectId(service_id)})
        
        # Convert _id to string for response
        updated_service["id"] = str(updated_service.pop("_id"))
        return ServiceResponse(**updated_service)
        
    except Exception as e:
        logger.error(f"Error updating service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{service_id}")
async def delete_service(service_id: str):
    try:
        result = await db.get_collection("services").delete_one({"_id": ObjectId(service_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
            
        return {"message": "Service deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 