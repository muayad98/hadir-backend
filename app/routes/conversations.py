from fastapi import APIRouter, HTTPException, Query, Body
from bson import ObjectId

from app.models.conversations import Message, ConversationResponse
from app.logic.conversation_utils import get_conversation, add_message
from app.db import db

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/{customer_id}/add_message")
async def add_message_to_conversation(
    customer_id: str,
    business_id: str = Query(...),
    message: Message = Body(...)
) -> ConversationResponse:
    # Validate business exists
    business = await db.get_collection("businesses").find_one({"_id": ObjectId(business_id)})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Validate customer exists
    customer = await db.get_collection("customers").find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Add message to conversation
    conversation = await add_message(business_id, customer_id, message)
    if not conversation:
        raise HTTPException(status_code=500, detail="Failed to add message to conversation")
    return ConversationResponse(**conversation)

@router.get("/{customer_id}")
async def get_customer_conversation(
    customer_id: str,
    business_id: str = Query(...)
) -> ConversationResponse:
    conversation = await get_conversation(business_id, customer_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse(**conversation)

@router.get("/")
async def get_business_conversations(
    business_id: str = Query(...)
) -> list[ConversationResponse]:
    collection = db.get_collection("conversations")
    conversations = await collection.find({"business_id": ObjectId(business_id)}).to_list(None)
    # Convert _id to id for each conversation
    for conv in conversations:
        conv["id"] = conv.pop("_id")
    return [ConversationResponse(**conv) for conv in conversations] 