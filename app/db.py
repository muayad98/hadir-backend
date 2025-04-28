from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls, mongodb_url: str):
        try:
            # Connect with minimal configuration
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,
                tls=True,
                tlsInsecure=True
            )
            
            # Test the connection
            await cls.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            cls.db = cls.client.hadir
            
            # Create indexes
            await cls._init_indexes()
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise e

    @classmethod
    async def _init_indexes(cls):
        # Business indexes
        await cls.db.businesses.create_index("whatsapp_number", unique=True)
        
        # Service indexes
        await cls.db.services.create_index("business_id")
        
        # Booking indexes
        await cls.db.bookings.create_index("business_id")
        await cls.db.bookings.create_index("start_time")
        await cls.db.bookings.create_index([
            ("business_id", 1),
            ("start_time", 1),
            ("end_time", 1)
        ])

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.db[collection_name]

db = Database()
