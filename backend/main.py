from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

# Import routes
from backend.routes.upload import router as upload_router
from backend.routes.calculate import router as calculate_router

# Initialize FastAPI app
app = FastAPI(title="FairShare API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Include routers
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(calculate_router, prefix="/api", tags=["calculate"])


@app.get("/")
async def serve_index():
    """Serve the main index page."""
    return FileResponse(str(frontend_path / "index.html"))


@app.get("/review.html")
async def serve_review():
    """Serve the review page."""
    return FileResponse(str(frontend_path / "review.html"))


@app.get("/result.html")
async def serve_result():
    """Serve the result page."""
    return FileResponse(str(frontend_path / "result.html"))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
