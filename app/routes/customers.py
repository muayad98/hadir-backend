from fastapi import APIRouter, HTTPException
from typing import List
from app.models.customers import CustomerCreate, CustomerResponse
from app.db import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=CustomerResponse)
async def create_or_update_customer(customer: CustomerCreate):
    # Get customers collection
    customers_collection = db.get_collection("customers")
    
    # Check if customer exists
    existing_customer = await customers_collection.find_one({"whatsapp_id": customer.whatsapp_id})
    
    if existing_customer:
        # Update existing customer
        update_data = customer.dict(exclude_unset=True)
        await customers_collection.update_one(
            {"whatsapp_id": customer.whatsapp_id},
            {"$set": update_data}
        )
        # Fetch updated document
        updated_customer = await customers_collection.find_one({"whatsapp_id": customer.whatsapp_id})
        # Convert ObjectId to string
        updated_customer["_id"] = str(updated_customer["_id"])
        return CustomerResponse(**updated_customer)
    else:
        # Create new customer
        customer_data = customer.dict()
        customer_data["created_at"] = datetime.utcnow()
        result = await customers_collection.insert_one(customer_data)
        
        # Fetch created document
        created_customer = await customers_collection.find_one({"_id": result.inserted_id})
        # Convert ObjectId to string
        created_customer["_id"] = str(created_customer["_id"])
        return CustomerResponse(**created_customer)

@router.get("/{whatsapp_id}", response_model=CustomerResponse)
async def get_customer(whatsapp_id: str):
    # Get customers collection
    customers_collection = db.get_collection("customers")
    
    customer = await customers_collection.find_one({"whatsapp_id": whatsapp_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    # Convert ObjectId to string
    customer["_id"] = str(customer["_id"])
    return CustomerResponse(**customer)

@router.get("/", response_model=List[CustomerResponse])
async def list_customers():
    # Get customers collection
    customers_collection = db.get_collection("customers")
    
    customers = await customers_collection.find().sort("created_at", -1).to_list(length=None)
    # Convert ObjectId to string for each customer
    for customer in customers:
        customer["_id"] = str(customer["_id"])
    return [CustomerResponse(**customer) for customer in customers] 