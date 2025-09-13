from datetime import datetime
from beanie import Document
from pydantic import Field


class MedianSalePrice(Document):
    city: str
    state: str
    last_updated_at: datetime = Field(default_factory=datetime.now)
    median_sale_data: dict[str, float]

    class Settings:
        collection_name = "median_sale_price"
        indexes = [
            "city",
            "state",
        ]
