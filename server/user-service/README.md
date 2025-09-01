# Users Service

A FastAPI-based microservice for managing user profiles (buyers and sellers) using MongoDB.

## Features

- Buyer profile management
- Seller profile management
- MongoDB integration using Beanie ODM
- RabbitMQ message queue integration
- Elasticsearch integration
- JWT authentication
- Health checks

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
- `GET /` - Health check

### Buyer Routes
- `GET /api/v1/buyer/email` - Get buyer by email
- `GET /api/v1/buyer/username` - Get current user's buyer profile
- `GET /api/v1/buyer/username/{username}` - Get buyer by username
- `PUT /api/v1/buyer/{buyerId}` - Update buyer profile

### Seller Routes
- `GET /api/v1/seller/id/{sellerId}` - Get seller by ID
- `GET /api/v1/seller/username/{username}` - Get seller by username
- `PUT /api/v1/seller/{sellerId}` - Update seller profile
- `POST /api/v1/seller/create/{sellerId}` - Create seller profile
- `POST /api/v1/seller/seed/{count}` - Seed random sellers

## Database

Uses MongoDB with Beanie ODM for document modeling and async operations.
