from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import qrcode
from io import BytesIO

from database import engine, get_db
from models import Base, URL, URLClick
from schemas import URLCreate, URLResponse, URLStats, URLListResponse
from utils import generate_short_code, is_valid_url

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A professional URL shortening service with analytics and QR codes",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to URL Shortener API",
        "documentation": "/docs",
        "endpoints": {
            "shorten": "POST /shorten",
            "redirect": "GET /{short_code}",
            "stats": "GET /stats/{short_code}",
            "qr_code": "GET /qr/{short_code}",
            "list_urls": "GET /urls"
        }
    }

@app.post("/shorten", response_model=URLResponse, tags=["URLs"])
async def shorten_url(url_data: URLCreate, db: Session = Depends(get_db)):
    if not is_valid_url(url_data.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    if url_data.custom_alias:
        existing = db.query(URL).filter(URL.short_code == url_data.custom_alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom alias already exists")
        short_code = url_data.custom_alias
    else:
        while True:
            short_code = generate_short_code()
            existing = db.query(URL).filter(URL.short_code == short_code).first()
            if not existing:
                break
    
    db_url = URL(
        original_url=url_data.original_url,
        short_code=short_code,
        expires_at=url_data.expires_at
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    return URLResponse(
        id=db_url.id,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=f"http://localhost:8000/{db_url.short_code}",
        created_at=db_url.created_at,
        expires_at=db_url.expires_at,
        click_count=0
    )

@app.get("/{short_code}", tags=["URLs"])
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    if url.expires_at and url.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This short URL has expired")
    
    click = URLClick(
        url_id=url.id,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    db.add(click)
    db.commit()
    
    return RedirectResponse(url=url.original_url, status_code=307)

@app.get("/stats/{short_code}", response_model=URLStats, tags=["Analytics"])
async def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    clicks = db.query(URLClick).filter(URLClick.url_id == url.id).all()
    
    referrers = {}
    user_agents = {}
    recent_clicks = []
    
    for click in clicks:
        ref = click.referrer or "Direct"
        referrers[ref] = referrers.get(ref, 0) + 1
        
        ua = click.user_agent or "Unknown"
        if "Chrome" in ua:
            browser = "Chrome"
        elif "Firefox" in ua:
            browser = "Firefox"
        elif "Safari" in ua:
            browser = "Safari"
        elif "Edge" in ua:
            browser = "Edge"
        else:
            browser = "Other"
        user_agents[browser] = user_agents.get(browser, 0) + 1
        
        if len(recent_clicks) < 10:
            recent_clicks.append({
                "timestamp": click.clicked_at,
                "referrer": click.referrer,
                "user_agent": click.user_agent
            })
    
    return URLStats(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"http://localhost:8000/{url.short_code}",
        created_at=url.created_at,
        expires_at=url.expires_at,
        click_count=len(clicks),
        referrers=referrers,
        user_agents=user_agents,
        recent_clicks=recent_clicks
    )

@app.get("/qr/{short_code}", tags=["QR Codes"])
async def generate_qr_code(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://localhost:8000/{short_code}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/urls", response_model=List[URLListResponse], tags=["URLs"])
async def list_urls(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    urls = db.query(URL).offset(skip).limit(limit).all()
    
    result = []
    for url in urls:
        click_count = db.query(URLClick).filter(URLClick.url_id == url.id).count()
        result.append(URLListResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"http://localhost:8000/{url.short_code}",
            created_at=url.created_at,
            expires_at=url.expires_at,
            click_count=click_count
        ))
    
    return result

@app.delete("/urls/{short_code}", tags=["URLs"])
async def delete_url(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    db.query(URLClick).filter(URLClick.url_id == url.id).delete()
    db.delete(url)
    db.commit()
    
    return {"message": "URL deleted successfully"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
