import functools

from motor.motor_asyncio import AsyncIOMotorClient

from .configs import MONGODB_URL


@functools.lru_cache
def get_db_client() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,  # Set timeout to 5 seconds
    )
    return client
