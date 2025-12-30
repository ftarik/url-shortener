from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from contextlib import asynccontextmanager
import logging

from database import get_db, init_db, URL, Analytics
from schemas import URLCreate, URLResponse, AnalyticsResponse, AnalyticsEntry
from utils import generate_short_code, generate_qr_code, calculate_expiration_date, is_url_expired

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown (if needed)


# Initialize FastAPI app
app = FastAPI(
    title="URL Shortener Service",
    description="A professional FastAPI-based URL shortening service with analytics, QR codes, and expiration features.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with service information."""
    return {
        "service": "URL Shortener",
        "version": "1.0.0",
        "features": [
            "URL shortening",
            "Custom short codes",
            "Analytics tracking",
            "QR code generation",
            "URL expiration"
        ]
    }


@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED, tags=["URL"])
def shorten_url(url_data: URLCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a shortened URL.
    
    - **url**: The original URL to shorten
    - **custom_code**: Optional custom short code (alphanumeric, underscore, hyphen)
    - **expires_in_days**: Optional expiration in days (1-365)
    """
    # Generate or use custom short code
    if url_data.custom_code:
        short_code = url_data.custom_code
        # Check if custom code already exists
        existing = db.query(URL).filter(URL.short_code == short_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom short code already exists"
            )
    else:
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            existing = db.query(URL).filter(URL.short_code == short_code).first()
            if not existing:
                break
    
    # Calculate expiration date if provided
    expires_at = None
    if url_data.expires_in_days:
        expires_at = calculate_expiration_date(url_data.expires_in_days)
    
    # Create new URL entry
    db_url = URL(
        original_url=str(url_data.url),
        short_code=short_code,
        expires_at=expires_at
    )
    
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    # Build short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{short_code}"
    
    return URLResponse(
        id=db_url.id,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=short_url,
        created_at=db_url.created_at,
        expires_at=db_url.expires_at,
        is_active=bool(db_url.is_active)
    )


@app.get("/{short_code}", tags=["URL"])
def redirect_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Redirect to the original URL using the short code.
    Also tracks analytics data.
    """
    # Find URL by short code
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    # Check if URL is active
    if not url_entry.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This URL has been deactivated"
        )
    
    # Check if URL has expired
    if url_entry.expires_at and is_url_expired(url_entry.expires_at):
        url_entry.is_active = 0
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This URL has expired"
        )
    
    # Track analytics
    analytics_entry = Analytics(
        url_id=url_entry.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        referer=request.headers.get("referer")
    )
    
    db.add(analytics_entry)
    db.commit()
    
    logger.info(f"Redirecting {short_code} to {url_entry.original_url}")
    
    return RedirectResponse(url=url_entry.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/analytics/{short_code}", response_model=AnalyticsResponse, tags=["Analytics"])
def get_analytics(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Get analytics data for a shortened URL.
    
    Returns:
    - URL information
    - Total clicks
    - Detailed analytics entries
    """
    # Find URL by short code
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    # Get all analytics entries
    analytics_entries = db.query(Analytics).filter(Analytics.url_id == url_entry.id).all()
    
    # Build short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{short_code}"
    
    return AnalyticsResponse(
        url_info=URLResponse(
            id=url_entry.id,
            original_url=url_entry.original_url,
            short_code=url_entry.short_code,
            short_url=short_url,
            created_at=url_entry.created_at,
            expires_at=url_entry.expires_at,
            is_active=bool(url_entry.is_active)
        ),
        total_clicks=len(analytics_entries),
        analytics=[
            AnalyticsEntry(
                visited_at=entry.visited_at,
                user_agent=entry.user_agent,
                ip_address=entry.ip_address,
                referer=entry.referer
            )
            for entry in analytics_entries
        ]
    )


@app.get("/qr/{short_code}", tags=["QR Code"])
def get_qr_code(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Generate and return a QR code for the shortened URL.
    """
    # Find URL by short code
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    # Build short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{short_code}"
    
    # Generate QR code
    qr_buffer = generate_qr_code(short_url)
    
    return StreamingResponse(
        qr_buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={short_code}_qr.png"}
    )


@app.delete("/url/{short_code}", tags=["URL"])
def deactivate_url(short_code: str, db: Session = Depends(get_db)):
    """
    Deactivate a shortened URL (soft delete).
    """
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    url_entry.is_active = 0
    db.commit()
    
    return {"message": f"URL {short_code} has been deactivated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
