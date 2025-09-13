from fastapi import FastAPI
from app.routers.sale_price import router as sale_price_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Redfin Scraper",
    description="A FastAPI-based web scraping service that retrieves median sale price data for US cities from redfin.com. The API scrapes real estate data and stores it in MongoDB for efficient retrieval.",  # noqa: E501
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Realtor Scraper"}


app.include_router(sale_price_router, prefix="/sale-price", tags=["sale-price"])
