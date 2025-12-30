from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False, index=True)
    short_code = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    clicks = relationship("URLClick", back_populates="url", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<URL {self.short_code} -> {self.original_url}>"

class URLClick(Base):
    __tablename__ = "url_clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    referrer = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    url = relationship("URL", back_populates="clicks")
    
    def __repr__(self):
        return f"<URLClick {self.id} for URL {self.url_id}>"
