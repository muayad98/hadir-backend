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
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.db[collection_name]

db = Database()
