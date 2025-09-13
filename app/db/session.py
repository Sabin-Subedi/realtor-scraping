from app.config import settings
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.db.models import MedianSalePrice


async def init_db():
    logger.info(f"Initializing database with URI: {settings.MONGO_URI}")
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
    )
    await init_beanie(database=client.db_name, document_models=[MedianSalePrice])
    logger.success("Connected to MongoDB")
