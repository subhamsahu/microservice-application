# Auth Service API

A scalable, production-ready microservice built using **FastAPI**, with structured logging, environment-based config loading, and integration support for **Elasticsearch**.

---

## 📁 Project Structure

```
.
├── app/                     # Application package
│   ├── core/               # Core configs, constants, exceptions, logger, middlewares
│   ├── models/             # Pydantic models or ORM models
│   ├── respositories/      # Database or external data interaction layers
│   ├── routers/            # FastAPI route definitions
│   ├── schemas/            # Request/response schemas
│   ├── services/           # Business logic (e.g., Elasticsearch)
│   ├── utils/              # Helper utilities
│   └── main.py             # FastAPI app instance
├── cli/                    # CLI commands or utilities
├── dependencies/           # External dependency files (e.g., requirements.txt)
├── tests/                  # Unit and integration tests
├── server.py               # Entrypoint to run FastAPI app
├── app.log                 # Application logs
├── Dockerfile              # Production Dockerfile
├── Dockerfile.development # Development Dockerfile
├── pyproject.toml          # Poetry configuration
├── poetry.lock             # Poetry lockfile
└── README.md               # Project documentation
```

---

## 🚀 Features

* ✅ FastAPI framework for blazing-fast APIs
* ✅ Structured and thread-safe logger with Elasticsearch support
* ✅ Singleton logger for consistent logging
* ✅ Centralized exception and response handling
* ✅ Clean modular architecture
* ✅ Dockerized for container-based deployment
* ✅ Environment-based config using `.env` or `pyproject.toml`

---

## 🛠️ Setup Instructions

### Prerequisites

* Python 3.13+
* [Poetry](https://python-poetry.org/)
* Docker (optional, for containerization)

---

### 1. Clone and Install

```bash
git clone https://github.com/your-org/notification-service.git
cd notification-service
poetry install
```

---

### 2. Configure Environment

Add environment-specific config inside `app/core/config.py` or `.env` (if supported).

Set Elasticsearch flag to enable logging:

```python
ENABLE_ES = 1
ELASTICSEARCH_URL = "http://localhost:9200"
```

---

### 3. Run the App (Dev)

```bash
python server.py
```

Or using the FastAPI CLI:

```bash
fastapi dev server.py --host 0.0.0.0 --port 4001
```

---

### 4. Run in Docker

**Build:**

```bash
docker build -t notification-service -f Dockerfile .
```

**Run:**

```bash
docker run -p 8000:8000 notification-service
```

For development:

```bash
docker build -t notification-dev -f Dockerfile.development .
docker run -p 8000:8000 notification-dev
```

---

## 💪 Running Tests

```bash
poetry run pytest
```

---

## 📋 Logging

* Default log level: `INFO`
* Logs are written to `app.log`
* When `ENABLE_ES_LOGGING=1`, logs are also sent to Elasticsearch

---

## 🛆 Dependency Management

All dependencies are managed by [Poetry](https://python-poetry.org/):

```bash
poetry add <package-name>
```

---

## 🧐 Contributions

This project follows a modular structure to encourage scalability. PRs, issues, and discussions are welcome!

---

## 📄 License

[MIT License](LICENSE)

---
