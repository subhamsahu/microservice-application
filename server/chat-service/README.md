# Chat Service

A real-time messaging service for the microservice application architecture.

## Features

- Real-time chat messaging
- Message persistence
- User authentication integration
- WebSocket support for real-time communication
- Message history and retrieval

## Getting Started

### Prerequisites

- Python 3.13+
- Poetry for dependency management
- MongoDB for data persistence
- Redis for caching
- RabbitMQ for message queuing
- Elasticsearch (optional)

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration.

4. Run the service:
```bash
poetry run python server.py
```

## API Endpoints

- `GET /api/v1/chat/health` - Health check endpoint
- `POST /api/v1/chat/messages` - Send a message
- `GET /api/v1/chat/messages` - Get message history
- `GET /api/v1/chat/rooms` - Get chat rooms

## Configuration

The service can be configured using environment variables. See `.env.example` for available options.

## Development

For development, use:
```bash
poetry run python server.py
```

The service will run on `http://localhost:4004` by default.