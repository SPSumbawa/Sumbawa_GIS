from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import router as spatial_router
import uvicorn
import os

app = FastAPI(title="Sumbawa Parcel GIS API", version="1.0.0")

# Allow CORS for all (since Plugin might call from localhost or network)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router
app.include_router(spatial_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "service": "Sumbawa GIS API"}

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible from network
    # Must use app.main:app when running from root as module
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
