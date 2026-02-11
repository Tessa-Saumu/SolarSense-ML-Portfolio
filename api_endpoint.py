"""
FastAPI REST API for Solar Viability Analysis
This is what you deploy and give to users
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from orchestration_service import (
    analyze_business_for_solar,
    SolarViabilityOrchestrator,
    BusinessInput
)

# ============================================
# SETUP
# ============================================

app = FastAPI(
    title="Solar Viability API",
    description="AI-powered solar feasibility analysis for SMEs",
    version="1.0.0"
)

# Enable CORS (for web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SolarAnalysisRequest(BaseModel):
    """What the API accepts"""
    business_name: str = Field(..., description="Name of the business")
    location: str = Field(..., description="City/region location")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    monthly_energy_usage_kwh: float = Field(..., gt=0, description="Average monthly energy usage in kWh")
    monthly_energy_cost: float = Field(..., gt=0, description="Average monthly energy cost in KES")
    roof_area_sqm: float = Field(..., gt=0, description="Available roof area in square meters")
    business_type: str = Field(..., description="Type of business (e.g., 'Food & Beverage', 'Retail')")

    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Joe's Coffee Shop",
                "location": "Nairobi, Kenya",
                "latitude": -1.2921,
                "longitude": 36.8219,
                "monthly_energy_usage_kwh": 2500,
                "monthly_energy_cost": 45000,
                "roof_area_sqm": 150,
                "business_type": "Food & Beverage"
            }
        }


class SolarAnalysisResponse(BaseModel):
    """What the API returns"""
    solar_viable: bool = Field(..., description="Whether solar is recommended")
    recommended_system_size_kw: float = Field(..., description="Recommended system size in kW")
    estimated_roi_years: float = Field(..., description="Estimated return on investment in years")
    confidence_score: float = Field(..., description="Confidence in recommendation (0-100)")
    recommendation_summary: str = Field(..., description="Executive summary of recommendation")
    key_reasons: List[str] = Field(..., description="Main reasons for the recommendation")
    warnings: List[str] = Field(..., description="Risks or concerns to consider")
    next_steps: List[str] = Field(..., description="Recommended next actions")
    analyzed_at: str = Field(..., description="Timestamp of analysis")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Solar Viability API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.post(
    "/api/v1/analyze",
    response_model=SolarAnalysisResponse,
    tags=["Solar Analysis"],
    summary="Analyze solar viability for a business"
)
async def analyze_solar_viability(request: SolarAnalysisRequest):
    """
    **Analyze whether solar installation is viable for a business**

    This endpoint:
    1. Calls AI Model 1 for solar potential analysis
    2. Calls AI Model 2 for cost and ROI analysis
    3. Calls AI Model 3 for business suitability analysis
    4. Applies decision rules to determine viability
    5. Returns comprehensive recommendation with explanation

    **Example Request:**
    ```json
    {
      "business_name": "Joe's Coffee Shop",
      "location": "Nairobi, Kenya",
      "latitude": -1.2921,
      "longitude": 36.8219,
      "monthly_energy_usage_kwh": 2500,
      "monthly_energy_cost": 45000,
      "roof_area_sqm": 150,
      "business_type": "Food & Beverage"
    }
    ```

    **Returns:**
    - Viability decision (yes/no)
    - Recommended system size
    - ROI estimate
    - Detailed explanation
    - Next steps
    """

    try:
        logger.info(f"Received analysis request for: {request.business_name}")

        # Call orchestration service
        result = await analyze_business_for_solar(
            business_name=request.business_name,
            location=request.location,
            latitude=request.latitude,
            longitude=request.longitude,
            monthly_energy_usage_kwh=request.monthly_energy_usage_kwh,
            monthly_energy_cost=request.monthly_energy_cost,
            roof_area_sqm=request.roof_area_sqm,
            business_type=request.business_type
        )

        logger.info(
            f"Analysis complete for {request.business_name}: "
            f"{'VIABLE' if result['solar_viable'] else 'NOT VIABLE'}"
        )

        return result

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post(
    "/api/v1/batch-analyze",
    tags=["Solar Analysis"],
    summary="Analyze multiple businesses (batch processing)"
)
async def batch_analyze(
    requests: List[SolarAnalysisRequest],
    background_tasks: BackgroundTasks
):
    """
    Analyze multiple businesses in one request
    Good for portfolio analysis
    """

    if len(requests) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 businesses per batch request"
        )

    results = []

    for req in requests:
        try:
            result = await analyze_business_for_solar(
                business_name=req.business_name,
                location=req.location,
                latitude=req.latitude,
                longitude=req.longitude,
                monthly_energy_usage_kwh=req.monthly_energy_usage_kwh,
                monthly_energy_cost=req.monthly_energy_cost,
                roof_area_sqm=req.roof_area_sqm,
                business_type=req.business_type
            )
            results.append({
                "business_name": req.business_name,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "business_name": req.business_name,
                "status": "failed",
                "error": str(e)
            })

    return {
        "total_analyzed": len(requests),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }


@app.get(
    "/api/v1/thresholds",
    tags=["Configuration"],
    summary="Get current decision thresholds"
)
async def get_thresholds():
    """
    Returns the current decision thresholds used by the engine
    Useful for understanding how decisions are made
    """
    from orchestration_service import DecisionEngine

    return {
        "min_solar_score": DecisionEngine.MIN_SOLAR_SCORE,
        "max_roi_years": DecisionEngine.MAX_ROI_YEARS,
        "min_suitability_score": DecisionEngine.MIN_SUITABILITY_SCORE,
        "min_confidence": DecisionEngine.MIN_CONFIDENCE,
        "description": {
            "min_solar_score": "Minimum solar potential score (0-10) required",
            "max_roi_years": "Maximum acceptable ROI period in years",
            "min_suitability_score": "Minimum business suitability score (0-10) required",
            "min_confidence": "Minimum model confidence (0-100) required"
        }
    }


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(Exception)
async def general_error_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail="An unexpected error occurred. Please try again."
    )


# ============================================
# STARTUP/SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Solar Viability API starting up...")
    logger.info("📚 API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Solar Viability API shutting down...")


# ============================================
# RUN SERVER (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_endpoint:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
