from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from app.db.models import MedianSalePrice
from app.schemas import MedianSaleRequest
from app.scrapers.sales_median_price import sales_median_price_scraper

router = APIRouter()


@router.get("/")
async def get_sale_price(request_data: Annotated[MedianSaleRequest, Query()]):
    median_sale_price = await MedianSalePrice.find_one(
        MedianSalePrice.city == request_data.city,
        MedianSalePrice.state == request_data.state,
    )
    if median_sale_price:
        return median_sale_price

    median_sale_data = await sales_median_price_scraper.scrape(
        request_data.city, request_data.state
    )

    if median_sale_data and median_sale_data[0].regionName is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to scrape median sale price data. Please try again later.",
        )

    city, state = median_sale_data[0].regionName.split(", ")

    median_sale_data_dict = {}
    for data in median_sale_data:
        median_sale_data_dict[data.date.strftime("%Y-%m")] = data.value

    median_sale_price = await MedianSalePrice(
        city=city.strip(),
        state=state.strip(),
        median_sale_data=median_sale_data_dict,
        last_updated_at=datetime.now(),
    ).save()

    return median_sale_price
