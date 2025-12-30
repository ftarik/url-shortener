# URL Shortener API

A professional FastAPI-based URL shortening service with analytics, QR codes, and expiration features.

## Features

- Shorten URLs with auto-generated or custom aliases
- Click analytics (visits, timestamps, referrers, user agents)
- QR code generation for each short URL
- URL expiration dates
- Statistics dashboard
- SQLite database with SQLAlchemy ORM
- Comprehensive API documentation
- Input validation with Pydantic

## Tech Stack

- FastAPI - Modern web framework
- SQLAlchemy - ORM for database operations
- Pydantic - Data validation
- qrcode - QR code generation
- SQLite - Database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-shortener-api.git
cd url-shortener-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Create Short URL
```bash
POST /shorten
{
  "original_url": "https://example.com",
  "custom_alias": "mylink",
  "expires_at": "2024-12-31T23:59:59"
}
```

### Redirect to Original URL
```bash
GET /{short_code}
```

### Get URL Statistics
```bash
GET /stats/{short_code}
```

### Get QR Code
```bash
GET /qr/{short_code}
```

### List All URLs
```bash
GET /urls?skip=0&limit=100
```

### Delete URL
```bash
DELETE /urls/{short_code}
```

## Example Usage

```python
import requests

# Shorten a URL
response = requests.post(
    "http://localhost:8000/shorten",
    json={
        "original_url": "https://www.example.com/very/long/url",
        "custom_alias": "example"
    }
)
print(response.json())

# Get statistics
stats = requests.get("http://localhost:8000/stats/example")
print(stats.json())
```

## Project Structure

```
url-shortener-api/
├── main.py
├── models.py
├── schemas.py
├── database.py
├── utils.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Contact

Your Name - your.email@example.com

Project Link: https://github.com/yourusername/url-shortener-api
