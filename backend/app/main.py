from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import experiments
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Persona Validator", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Persona Validator API"}