# URL Shortener Service

A professional FastAPI-based URL shortening service with analytics, QR codes, and expiration features.

## Features

- 🔗 **URL Shortening**: Convert long URLs into short, manageable links
- 🎨 **Custom Short Codes**: Create personalized short codes for your URLs
- 📊 **Analytics Tracking**: Track clicks, user agents, IP addresses, and referrers
- 🔲 **QR Code Generation**: Generate QR codes for shortened URLs
- ⏰ **URL Expiration**: Set expiration dates for temporary links
- 🔒 **URL Management**: Deactivate URLs when needed
- 📚 **API Documentation**: Interactive API docs with Swagger UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ftarik/url-shortener.git
cd url-shortener
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Create Shortened URL

**POST** `/shorten`

Create a shortened URL with optional custom code and expiration.

**Request Body:**
```json
{
  "url": "https://example.com/very/long/url",
  "custom_code": "mycode",  // Optional
  "expires_in_days": 30     // Optional (1-365 days)
}
```

**Response:**
```json
{
  "id": 1,
  "original_url": "https://example.com/very/long/url",
  "short_code": "mycode",
  "short_url": "http://localhost:8000/mycode",
  "created_at": "2025-12-30T12:00:00",
  "expires_at": "2025-01-29T12:00:00",
  "is_active": true
}
```

### 2. Redirect to Original URL

**GET** `/{short_code}`

Redirects to the original URL and tracks analytics.

**Example:**
```bash
curl -L http://localhost:8000/mycode
```

### 3. Get Analytics

**GET** `/analytics/{short_code}`

Retrieve analytics data for a shortened URL.

**Response:**
```json
{
  "url_info": {
    "id": 1,
    "original_url": "https://example.com/very/long/url",
    "short_code": "mycode",
    "short_url": "http://localhost:8000/mycode",
    "created_at": "2025-12-30T12:00:00",
    "expires_at": "2025-01-29T12:00:00",
    "is_active": true
  },
  "total_clicks": 5,
  "analytics": [
    {
      "visited_at": "2025-12-30T12:01:00",
      "user_agent": "Mozilla/5.0...",
      "ip_address": "127.0.0.1",
      "referer": "https://google.com"
    }
  ]
}
```

### 4. Generate QR Code

**GET** `/qr/{short_code}`

Generate a QR code image for the shortened URL.

**Example:**
```bash
curl http://localhost:8000/qr/mycode -o qrcode.png
```

### 5. Deactivate URL

**DELETE** `/url/{short_code}`

Deactivate a shortened URL (soft delete).

**Response:**
```json
{
  "message": "URL mycode has been deactivated"
}
```

## Example Usage

### Using cURL

```bash
# Create a shortened URL
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Create with custom code and expiration
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "custom_code": "demo",
    "expires_in_days": 7
  }'

# Get analytics
curl "http://localhost:8000/analytics/demo"

# Download QR code
curl "http://localhost:8000/qr/demo" -o demo_qr.png

# Deactivate URL
curl -X DELETE "http://localhost:8000/url/demo"
```

### Using Python

```python
import requests

# Create shortened URL
response = requests.post(
    "http://localhost:8000/shorten",
    json={
        "url": "https://example.com",
        "custom_code": "demo",
        "expires_in_days": 30
    }
)
short_url_data = response.json()
print(f"Short URL: {short_url_data['short_url']}")

# Get analytics
analytics = requests.get(
    f"http://localhost:8000/analytics/{short_url_data['short_code']}"
).json()
print(f"Total clicks: {analytics['total_clicks']}")

# Download QR code
qr_response = requests.get(
    f"http://localhost:8000/qr/{short_url_data['short_code']}"
)
with open("qr_code.png", "wb") as f:
    f.write(qr_response.content)
```

## Database

The application uses SQLite by default with the following schema:

### URLs Table
- `id`: Primary key
- `original_url`: The original long URL
- `short_code`: Unique short code
- `created_at`: Creation timestamp
- `expires_at`: Optional expiration timestamp
- `is_active`: Active status (1 = active, 0 = deactivated)

### Analytics Table
- `id`: Primary key
- `url_id`: Foreign key to URLs table
- `visited_at`: Visit timestamp
- `user_agent`: Browser/client user agent
- `ip_address`: Visitor IP address
- `referer`: Referring URL

## Configuration

The database URL can be changed in `database.py`:
```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./url_shortener.db"
```

For production, consider using PostgreSQL or MySQL:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

## Project Structure

```
url-shortener/
├── main.py           # FastAPI application and endpoints
├── database.py       # Database models and setup
├── schemas.py        # Pydantic schemas for validation
├── utils.py          # Utility functions (QR, short code generation)
├── requirements.txt  # Python dependencies
├── .gitignore       # Git ignore file
└── README.md        # Documentation
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **QRCode**: QR code generation library
- **Uvicorn**: ASGI server implementation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.