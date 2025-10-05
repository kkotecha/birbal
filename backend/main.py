"""FastAPI application for BNS Section Predictor"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from graph.bns_workflow import predict_bns

app = FastAPI(
    title="Birbal - BNS Section Predictor",
    description="AI assistant for Indian police officers to identify applicable BNS sections",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://neobirbal.vercel.app",
        "https://birbal.vercel.app",
        "https://birbal-*.vercel.app",  # Vercel preview deployments
        "http://localhost:3000",  # Local development
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class PredictionRequest(BaseModel):
    """Request model for BNS prediction"""
    crime_description: str

    class Config:
        json_schema_extra = {
            "example": {
                "crime_description": "एक व्यक्ति ने घर में घुसकर सोना चुरा लिया"
            }
        }


class SectionPrediction(BaseModel):
    """Individual section prediction"""
    section_number: str
    section_title: str
    confidence: float
    reasoning: str


class PredictionResponse(BaseModel):
    """Response model for BNS prediction"""
    raw_description: str
    refined_description: str
    predictions: List[Dict]
    success: bool
    error: Optional[str] = None


# Routes
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Birbal BNS Predictor",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_bns_sections(request: PredictionRequest):
    """
    Predict applicable BNS sections for a crime description.

    Args:
        request: Crime description

    Returns:
        Predictions with confidence scores
    """
    try:
        # Run workflow
        result = predict_bns(request.crime_description)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "raw_description": result["raw_description"],
            "refined_description": result["refined_description"],
            "predictions": result["predictions"],
            "success": True,
            "error": None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sections/{section_number}")
def get_section_details(section_number: str):
    """Get details for a specific BNS section"""
    from tools.vector_search import BNSVectorSearch

    searcher = BNSVectorSearch()
    section = searcher.get_section_details(section_number)

    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    return section


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
