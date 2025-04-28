from typing import Optional
from bson import ObjectId
from fastapi import HTTPException

from app.db import db
from app.models.conversations import Message, ConversationInDB

async def get_conversation(business_id: str, customer_id: str) -> Optional[dict]:
    """Get a conversation between a business and customer."""
    collection = db.get_collection("conversations")
    conversation = await collection.find_one({
        "business_id": ObjectId(business_id),
        "customer_id": ObjectId(customer_id)
    })
    if conversation:
        # Convert _id to id for Pydantic model
        conversation["id"] = conversation.pop("_id")
    return conversation

async def add_message(business_id: str, customer_id: str, message: Message) -> dict:
    """Add a message to a conversation, creating it if it doesn't exist."""
    try:
        collection = db.get_collection("conversations")
        
        # Use findOneAndUpdate with upsert for atomic operation
        result = await collection.find_one_and_update(
            {
                "business_id": ObjectId(business_id),
                "customer_id": ObjectId(customer_id)
            },
            {
                "$push": {"messages": message.dict()}
            },
            upsert=True,
            return_document=True
        )
        
        if result:
            # Convert _id to id for Pydantic model
            result["id"] = result.pop("_id")
            return result
        
        raise HTTPException(status_code=500, detail="Failed to add message to conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 