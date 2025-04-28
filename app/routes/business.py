from fastapi import APIRouter, HTTPException
from typing import List
from app.models.business import BusinessCreate, BusinessResponse, BusinessInDB
from app.db import db
from bson import ObjectId
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=BusinessResponse)
async def create_business(business: BusinessCreate):
    try:
        # Convert Pydantic model to dict
        business_dict = business.model_dump()
        
        # Check if business with same name exists
        existing_business = await db.get_collection("businesses").find_one({"name": business_dict["name"]})
        if existing_business:
            # Update existing business
            logger.info(f"Existing business found: {existing_business is not None}")
            result = await db.get_collection("businesses").update_one(
                {"_id": existing_business["_id"]},
                {"$set": business_dict}
            )
            logger.info(f"Updated document: {await db.get_collection('businesses').find_one({'_id': existing_business['_id']})}")
            
            # Convert _id to string for response
            business_dict["id"] = str(existing_business["_id"])
            return BusinessResponse(**business_dict)
        
        # Insert new business
        result = await db.get_collection("businesses").insert_one(business_dict)
        
        # Get the inserted document
        inserted_business = await db.get_collection("businesses").find_one({"_id": result.inserted_id})
        
        # Convert _id to string for response
        business_dict["id"] = str(result.inserted_id)
        return BusinessResponse(**business_dict)
        
    except Exception as e:
        logger.error(f"Error creating business: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[BusinessResponse])
async def get_businesses():
    try:
        businesses = []
        async for business in db.get_collection("businesses").find():
            # Convert _id to string for response
            business["id"] = str(business.pop("_id"))
            businesses.append(BusinessResponse(**business))
        return businesses
    except Exception as e:
        logger.error(f"Error getting businesses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str):
    try:
        business = await db.get_collection("businesses").find_one({"_id": ObjectId(business_id)})
        if business is None:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Convert _id to string for response
        business["id"] = str(business.pop("_id"))
        return BusinessResponse(**business)
    except Exception as e:
        logger.error(f"Error getting business: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 