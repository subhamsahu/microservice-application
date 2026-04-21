
# Catalog Service

A FastAPI-based microservice for managing seller catalogs (service/product listings) with advanced search and filtering, using MongoDB and Elasticsearch.

## Features

- Catalog (listing) creation, update, delete
- Advanced search with filters (query, price, delivery time, etc.)
- Category and subcategory support
- Tagging and rating system
- MongoDB integration via Beanie ODM
- Elasticsearch integration for fast search
- RabbitMQ integration for messaging
- JWT authentication for protected endpoints
- Health check endpoint

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables in `.env` file

3. Run the service:
```bash
poetry run python server.py
```


## API Endpoints

### Health
- `GET /health` — Service and dependency health check

### Catalog Endpoints
- `POST /create` — Create a new catalog (listing)
- `GET /search` — Search catalogs (query, price, delivery_time, etc.)
- `GET /search/category` — Search catalogs by category
- `GET /search/more_like/{category_id}` — Get similar catalogs
- `GET /{catalog_id}` — Get catalog by ID
- `PUT /{catalog_id}` — Update catalog by ID
- `DELETE /{catalog_id}` — Delete catalog by ID

All endpoints (except health/search) require authentication.

## Database

Uses MongoDB (Beanie ODM) for storing catalog listings. Each catalog includes:
- Seller ID
- Title, description, basic info
- Categories, subcategories, tags
- Price, cover image, expected delivery
- Ratings (with breakdown)
- Timestamps

Elasticsearch is used for fast, flexible search and filtering.
