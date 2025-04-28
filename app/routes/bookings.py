from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from datetime import datetime, timedelta
import pytz

from app.models.bookings import BookingCreate, BookingResponse, BookingUpdate
from app.db import db
from app.logic.booking_utils import get_service_duration, get_business, to_local, within_working_hours, overlap_exists

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, created_via: str = "admin"):
    try:
        biz = await get_business(booking.business_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Business not found")

    try:
        duration = await get_service_duration(booking.service_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Service not found")

    start_utc = booking.start_time
    tz_str = biz["timezone"]
    start_local = to_local(start_utc, tz_str)
    end_local = start_local + timedelta(minutes=duration)

    if not within_working_hours(start_local, end_local, biz["working_hours"]):
        raise HTTPException(status_code=400, detail="Outside business working hours")

    buffer = biz.get("buffer_minutes", 0)
    window_start = start_utc - timedelta(minutes=buffer)
    window_end = (start_utc + timedelta(minutes=duration)) + timedelta(minutes=buffer)

    if await overlap_exists(booking.business_id, window_start, window_end):
        raise HTTPException(status_code=409, detail="Time slot not available")

    now = datetime.utcnow()
    booking_doc = booking.model_dump(by_alias=True)
    booking_doc.update({
        "end_time": start_utc + timedelta(minutes=duration),
        "status": "confirmed",
        "created_via": created_via,
        "created_at": now,
        "updated_at": now
    })
    result = await db.get_collection("bookings").insert_one(booking_doc)
    doc = await db.get_collection("bookings").find_one({"_id": result.inserted_id})
    doc["id"] = str(doc.pop("_id"))
    return BookingResponse(**doc)

@router.get("/", response_model=list[BookingResponse])
async def list_bookings(business_id: str = Query(...)):
    if not await db.get_collection("businesses").find_one({"_id": ObjectId(business_id)}):
        raise HTTPException(status_code=404, detail="Business not found")

    cursor = db.get_collection("bookings").find({"business_id": business_id}).sort("start_time", 1)
    results = []
    async for b in cursor:
        b["id"] = str(b.pop("_id"))
        results.append(BookingResponse(**b))
    return results

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: str, update: BookingUpdate):
    data = update.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    data["updated_at"] = datetime.utcnow()
    result = await db.get_collection("bookings").update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    doc = await db.get_collection("bookings").find_one({"_id": ObjectId(booking_id)})
    doc["id"] = str(doc.pop("_id"))
    return BookingResponse(**doc)

@router.delete("/{booking_id}")
async def delete_booking(booking_id: str):
    result = await db.get_collection("bookings").delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted"} 