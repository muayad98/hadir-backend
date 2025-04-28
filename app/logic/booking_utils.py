from datetime import datetime, timedelta, time
import pytz
from app.db import db
from bson import ObjectId

async def get_service_duration(service_id: str) -> int:
    svc = await db.get_collection("services").find_one({"_id": ObjectId(service_id)})
    if not svc:
        raise ValueError("Service not found")
    return svc["duration_minutes"]

async def get_business(business_id: str):
    biz = await db.get_collection("businesses").find_one({"_id": ObjectId(business_id)})
    if not biz:
        raise ValueError("Business not found")
    return biz

def to_local(dt_utc: datetime, tz_str: str) -> datetime:
    tz = pytz.timezone(tz_str)
    if dt_utc.tzinfo is None:
        dt_utc = pytz.UTC.localize(dt_utc)
    return dt_utc.astimezone(tz)

def within_working_hours(start_local: datetime, end_local: datetime, working_hours: list) -> bool:
    day = start_local.weekday()
    print(f"Checking day {day} for time {start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}")
    
    # working_hours: list of dicts with 'day', 'start', 'end'
    slots = [w for w in working_hours if w["day"] == day]
    if not slots:
        print(f"No working hours found for day {day}")
        return False
        
    slot = slots[0]
    print(f"Found slot: {slot['start']} - {slot['end']}")
    
    # Create timezone-aware datetime objects for comparison
    tz = start_local.tzinfo
    start_work = datetime.combine(start_local.date(), time.fromisoformat(slot["start"]))
    end_work = datetime.combine(start_local.date(), time.fromisoformat(slot["end"]))
    
    # Make the times timezone-aware
    start_work = tz.localize(start_work)
    end_work = tz.localize(end_work)
    
    print(f"Comparing: {start_work.strftime('%H:%M')} <= {start_local.strftime('%H:%M')} and {end_local.strftime('%H:%M')} <= {end_work.strftime('%H:%M')}")
    
    is_within = start_work <= start_local and end_local <= end_work
    print(f"Result: {is_within}")
    return is_within

async def overlap_exists(business_id: str, window_start: datetime, window_end: datetime) -> bool:
    query = {
        "business_id": business_id,
        "status": "confirmed",
        "$or": [
            {"start_time": {"$lt": window_end}, "end_time": {"$gt": window_start}}
        ]
    }
    count = await db.get_collection("bookings").count_documents(query)
    return count > 0 