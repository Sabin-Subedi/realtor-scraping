# Realtor Scrape API

A FastAPI-based web scraping service that retrieves median sale price data for US cities from realtor.com. The API scrapes real estate data and stores it in MongoDB for efficient retrieval.

## Features

- **Web Scraping**: Automated scraping of median sale price data from realtor.com
- **RESTful API**: FastAPI-based API with automatic OpenAPI documentation
- **Database Storage**: MongoDB integration for data persistence and caching
- **Docker Support**: Containerized application with Docker Compose
- **Input Validation**: State validation using US state abbreviations
- **CORS Support**: Cross-origin resource sharing enabled

## Prerequisites

- Python 3.13+
- Docker and Docker Compose
- MongoDB (included in Docker Compose)

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtor-scrape
   ```

2. **Copy .env.example as .env**
    ```bash
    cp .env.example .env
    ```
    > You can update .env as per your configuration. Optionally you can add WEBSHARE_ROTATING_PROXY_URL (webshare proxy url that provides rotating proxy or you can pass any other proxy url).

4. **Start the services**
   ```bash
   docker-compose up -d
   ```

5. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive API Documentation: `http://localhost:8000/docs`
   - Alternative API Documentation: `http://localhost:8000/redoc`

## Manual Setup (Development)

1. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

2. **Install Playwright browsers**
   ```bash
   uv run playwright install --with-deps chromium
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   MONGODB_URL=mongodb://localhost:27017/realtor_scrape
   ```

4. **Start MongoDB**
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   
   # Or using local MongoDB installation
   mongod
   ```

5. **Run the application**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## API Usage

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
Visit `http://localhost:8000/docs` for the Swagger UI interface where you can:
- View all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

### Endpoints

#### 1. Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Hello, World!"
}
```

#### 2. Get Median Sale Price
```http
GET /sale-price/?city={city}&state={state}
```

**Parameters:**
- `city` (string, required): Name of the city
- `state` (string, required): US state abbreviation (e.g., "CA", "NY", "TX")

**Example Request:**
```bash
curl "http://localhost:8000/sale-price/?city=San Francisco&state=CA"
```

**Example Response:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "city": "San Francisco",
  "state": "CA",
  "last_updated_at": "2024-01-15T10:30:00Z",
  "median_sale_data": {
    "2023-01": 1250000.0,
    "2023-02": 1280000.0,
    "2023-03": 1300000.0,
    "2023-04": 1320000.0,
    "2023-05": 1350000.0,
    "2023-06": 1380000.0,
    "2023-07": 1400000.0,
    "2023-08": 1420000.0,
    "2023-09": 1450000.0,
    "2023-10": 1480000.0,
    "2023-11": 1500000.0,
    "2023-12": 1520000.0
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid state abbreviation
- `400 Bad Request`: Failed to scrape data

### Supported States
The API accepts all US state abbreviations:
```
AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY
```

## Data Model

### MedianSalePrice Document
```json
{
  "city": "string",
  "state": "string", 
  "last_updated_at": "datetime",
  "median_sale_data": {
    "YYYY-MM": "float"
  }
}
```

## Architecture

- **FastAPI**: Web framework for building the API
- **MongoDB**: Document database for data storage
- **Beanie**: ODM for MongoDB with Pydantic integration
- **Playwright**: Web scraping automation
- **Docker**: Containerization for easy deployment

## Development

### Project Structure
```
realtor-scrape/
├── app/
│   ├── db/
│   │   ├── models.py          # Database models
│   │   └── session.py         # Database connection
│   ├── routers/
│   │   └── sale_price.py      # API routes
│   ├── scrapers/
│   │   └── sales_median_price.py  # Web scraping logic
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI application
│   └── schemas.py             # Pydantic models
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Container definition
└── pyproject.toml            # Project dependencies
```

### Adding New Features
1. Create new routers in `app/routers/`
2. Add database models in `app/db/models.py`
3. Define schemas in `app/schemas.py`
4. Implement scrapers in `app/scrapers/`

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running on port 27017
   - Check the `MONGODB_URL` environment variable

2. **Playwright Installation Issues**
   - Run `uv run playwright install --with-deps chromium`
   - Ensure system dependencies are installed

3. **Scraping Failures**
   - The target website might have changed its structure
   - Check network connectivity
   - Verify the city/state combination exists

### Logs
View application logs:
```bash
docker-compose logs -f app
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
