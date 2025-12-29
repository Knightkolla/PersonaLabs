from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_persona_validator.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class ExperimentDB(Base):
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_context = Column(Text)  # JSON string
    feature_description = Column(Text)  # JSON string
    personas = Column(Text)  # JSON string
    simulation_results = Column(Text)  # JSON string
    aggregated_insights = Column(Text, nullable=True)  # JSON string
    is_public = Column(Boolean, default=False)
    share_token = Column(String, nullable=True, index=True)

class SimulationCacheDB(Base):
    __tablename__ = "simulation_cache"
    
    id = Column(String, primary_key=True, index=True)
    persona_hash = Column(String, index=True)
    feature_hash = Column(String, index=True)
    response = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()