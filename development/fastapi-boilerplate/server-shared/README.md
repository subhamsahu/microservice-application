# server-shared

**Reusable shared utilities for backend services**, including logging, Cloudinary uploads, FastAPI middleware, and error handling.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## Features

- **Singleton Logger** with optional Elasticsearch support
- **Cloudinary upload utility**
- **API Gateway verification middleware for FastAPI**
- **Custom error handler**
- **Miscellaneous reusable utility functions**

---

## 📁 Project Structure
server-shared
    ├── poetry.lock
    ├── pyproject.toml
    ├── README.md
    └── server-shared
        ├── __init__.py
        ├── cloudinary_upload.py
        ├── error_handler.py
        ├── gateway_middleware.py
        ├── logger.py
        └── utils.py

## Installation

### Option 1: Local Development

```bash
cd server-shared
poetry install
```

## Option 2: Use as Dependency (from another project)

using local path
```bash
poetry add ../server-shared/
```

using built wheel
```bash
cd server-shared
poetry build
pip install dist/server-shared-0.1.0-py3-none-any.whl
```

## usage 
```python
from server-shared import Logger, upload_to_cloudinary, verify_gateway_request

# Logger
logger = Logger()
logger.info("Application started.")

# Upload file to Cloudinary
# response = upload_to_cloudinary(file_path="example.jpg", public_id="uploads/example")

# FastAPI Middleware
# app.middleware("http")(verify_gateway_request)
```

