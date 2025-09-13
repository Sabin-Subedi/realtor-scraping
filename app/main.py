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
