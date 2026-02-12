"""
SECURE Solar Viability API - With Full Security Implementation
Implements: API Key Auth, Rate Limiting, Input Validation, Error Handling
"""

from fastapi import FastAPI, HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# ============================================
# SECURITY CONFIGURATION
# ============================================

# API Key Authentication (from .env file)
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY must be set in .env file!")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate Limiting (100 requests per minute)
limiter = Limiter(key_func=get_remote_address)

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# SETUP FASTAPI APP
# ============================================

app = FastAPI(
    title="Secure Solar Viability API",
    description="AI-powered solar feasibility analysis with enterprise security",
    version="2.0.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS (configure for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: Replace with actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# SECURITY FUNCTION: API KEY VALIDATION
# ============================================

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    SECURITY: Verify API key from X-API-Key header
    """
    if api_key is None:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header."
        )

    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return api_key


# ============================================
# INPUT VALIDATION: REQUEST MODEL
# ============================================

class SolarAnalysisRequest(BaseModel):
    """
    SECURITY: Strict input validation with realistic ranges
    """
    business_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the business"
    )

    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="City/region location"
    )

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude coordinate"
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude coordinate"
    )

    monthly_energy_usage_kwh: float = Field(
        ...,
        gt=0,
        le=1000000,  # SECURITY: Max 1M kWh/month (very large business)
        description="Average monthly energy usage in kWh"
    )

    monthly_energy_cost: float = Field(
        ...,
        gt=0,
        le=50000000,  # SECURITY: Max 50M KES/month
        description="Average monthly energy cost in KES"
    )

    roof_area_sqm: float = Field(
        ...,
        gt=0,
        le=100000,  # SECURITY: Max 100k sqm (very large building)
        description="Available roof area in square meters"
    )

    business_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of business"
    )

    # SECURITY: Custom validators
    @field_validator('monthly_energy_usage_kwh')
    @classmethod
    def validate_energy_usage(cls, v):
        """Ensure energy usage is realistic"""
        if v < 10:
            raise ValueError("Monthly energy usage too low (minimum 10 kWh)")
        if v > 1000000:
            raise ValueError("Monthly energy usage unrealistic (maximum 1,000,000 kWh)")
        return v

    @field_validator('roof_area_sqm')
    @classmethod
    def validate_roof_area(cls, v):
        """Ensure roof area is realistic"""
        if v < 5:
            raise ValueError("Roof area too small (minimum 5 sqm)")
        if v > 100000:
            raise ValueError("Roof area unrealistic (maximum 100,000 sqm)")
        return v

    @field_validator('monthly_energy_cost')
    @classmethod
    def validate_energy_cost_ratio(cls, v, values):
        """Ensure cost is reasonable relative to usage"""
        if 'monthly_energy_usage_kwh' in values:
            kwh = values['monthly_energy_usage_kwh']
            cost_per_kwh = v / kwh if kwh > 0 else 0

            # SECURITY: Realistic KES/kWh range (5-100)
            if cost_per_kwh < 5 or cost_per_kwh > 100:
                raise ValueError(
                    f"Energy cost per kWh ({cost_per_kwh:.2f} KES) is unrealistic. "
                    "Expected range: 5-100 KES/kWh"
                )
        return v

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


# ============================================
# OUTPUT VALIDATION: RESPONSE MODEL
# ============================================

class SolarAnalysisResponse(BaseModel):
    """
    SECURITY: Validated output format
    """
    solar_viable: bool
    recommended_system_size_kw: float = Field(..., ge=0, le=10000)
    estimated_roi_years: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    recommendation_summary: str
    key_reasons: List[str]
    warnings: List[str]
    next_steps: List[str]
    analyzed_at: str

    # SECURITY: Validate output ranges
    @field_validator('recommended_system_size_kw')
    @classmethod
    def validate_system_size(cls, v):
        """Ensure system size is realistic"""
        if v < 0 or v > 10000:
            raise ValueError("System size out of realistic range")
        return round(v, 2)

    @field_validator('estimated_roi_years')
    @classmethod
    def validate_roi(cls, v):
        """Ensure ROI is realistic"""
        if v < 0 or v > 100:
            raise ValueError("ROI years out of realistic range")
        return round(v, 2)

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is 0-100%"""
        if v < 0 or v > 100:
            raise ValueError("Confidence score must be 0-100")
        return round(v, 2)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


# ============================================
# IMPORT ORCHESTRATION SERVICE
# ============================================

try:
    from orchestration_service import analyze_business_for_solar
except ImportError:
    # Fallback if import fails
    logger.error("Could not import orchestration_service")
    async def analyze_business_for_solar(*args, **kwargs):
        raise HTTPException(
            status_code=500,
            detail="Service temporarily unavailable"
        )


# ============================================
# API ENDPOINTS WITH SECURITY
# ============================================

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint - NO AUTH REQUIRED"""
    return {
        "message": "Secure Solar Viability API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "security": "API Key required for analysis endpoints"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check - NO AUTH REQUIRED"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


@app.post(
    "/api/v1/analyze",
    response_model=SolarAnalysisResponse,
    tags=["Solar Analysis"],
    summary="Analyze solar viability (SECURE)",
    dependencies=[Security(verify_api_key)]  # SECURITY: Requires API key
)
@limiter.limit("100/minute")  # SECURITY: Rate limiting
async def analyze_solar_viability(
    request: Request,
    analysis_request: SolarAnalysisRequest
):
    """
    **SECURE ENDPOINT: Analyze solar viability for a business**

    **SECURITY FEATURES:**
    - ✅ API Key Authentication (X-API-Key header required)
    - ✅ Rate Limiting (100 requests/minute)
    - ✅ Input Validation (realistic ranges enforced)
    - ✅ Output Validation (safe data returned)
    - ✅ Error Handling (no internal details leaked)

    **Required Header:**
    - X-API-Key: Your API key

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
    """

    try:
        # Log request (without sensitive data)
        logger.info(f"Analysis request for: {analysis_request.business_name}")

        # SECURITY: Additional business logic validation
        if analysis_request.monthly_energy_usage_kwh > 50000:
            logger.warning(
                f"Very high energy usage: {analysis_request.monthly_energy_usage_kwh} kWh"
            )

        # Call orchestration service
        result = await analyze_business_for_solar(
            business_name=analysis_request.business_name,
            location=analysis_request.location,
            latitude=analysis_request.latitude,
            longitude=analysis_request.longitude,
            monthly_energy_usage_kwh=analysis_request.monthly_energy_usage_kwh,
            monthly_energy_cost=analysis_request.monthly_energy_cost,
            roof_area_sqm=analysis_request.roof_area_sqm,
            business_type=analysis_request.business_type
        )

        # SECURITY: Validate output before returning
        validated_result = SolarAnalysisResponse(**result)

        logger.info(
            f"Analysis complete: {analysis_request.business_name} - "
            f"{'VIABLE' if validated_result.solar_viable else 'NOT VIABLE'}"
        )

        return validated_result

    except ValueError as e:
        # SECURITY: 400 Bad Request for validation errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # SECURITY: 500 Internal Server Error - HIDE DETAILS
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please contact support."
        )


@app.post(
    "/api/v1/batch-analyze",
    tags=["Solar Analysis"],
    summary="Batch analyze multiple businesses (SECURE)",
    dependencies=[Security(verify_api_key)]  # SECURITY: Requires API key
)
@limiter.limit("20/minute")  # SECURITY: Lower limit for batch
async def batch_analyze(
    request: Request,
    requests_list: List[SolarAnalysisRequest]
):
    """
    **SECURE ENDPOINT: Analyze multiple businesses**

    **SECURITY:**
    - Maximum 50 businesses per batch
    - Slower rate limit (20/minute)
    """

    # SECURITY: Limit batch size
    if len(requests_list) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 businesses per batch request"
        )

    if len(requests_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty batch request"
        )

    results = []

    for req in requests_list:
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

            # SECURITY: Validate each result
            validated = SolarAnalysisResponse(**result)

            results.append({
                "business_name": req.business_name,
                "status": "success",
                "result": validated.dict()
            })

        except Exception as e:
            # SECURITY: Don't expose error details
            logger.error(f"Batch item error: {str(e)}")
            results.append({
                "business_name": req.business_name,
                "status": "failed",
                "error": "Processing error"
            })

    return {
        "total_analyzed": len(requests_list),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }


@app.get(
    "/api/v1/thresholds",
    tags=["Configuration"],
    summary="Get decision thresholds (SECURE)",
    dependencies=[Security(verify_api_key)]  # SECURITY: Requires API key
)
async def get_thresholds():
    """Get current decision thresholds - REQUIRES API KEY"""
    try:
        from orchestration_service import DecisionEngine

        return {
            "min_solar_score": DecisionEngine.MIN_SOLAR_SCORE,
            "max_roi_years": DecisionEngine.MAX_ROI_YEARS,
            "min_suitability_score": DecisionEngine.MIN_SUITABILITY_SCORE,
            "min_confidence": DecisionEngine.MIN_CONFIDENCE
        }
    except Exception as e:
        logger.error(f"Error fetching thresholds: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch configuration"
        )


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """SECURITY: Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Invalid input: {str(exc)}"}
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """SECURITY: Catch-all error handler - HIDE DETAILS"""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# ============================================
# STARTUP/SHUTDOWN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    logger.info(" Secure Solar Viability API starting up...")
    logger.info(f" API Key authentication: ENABLED")
    logger.info(f" Rate limiting: ENABLED (100/minute)")
    logger.info(f" Input validation: ENABLED")
    logger.info(" API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Secure Solar Viability API shutting down...")


# ============================================
# RUN SERVER (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "secure_api_endpoint:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
