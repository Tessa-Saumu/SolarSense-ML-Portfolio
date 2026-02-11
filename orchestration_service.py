"""
Solar Viability Orchestration Service
The BRAIN that coordinates all AI models and makes final decisions
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS (What we pass around)
# ============================================

@dataclass
class BusinessInput:
    """What the user sends us"""
    business_name: str
    location: str
    latitude: float
    longitude: float
    monthly_energy_usage_kwh: float
    monthly_energy_cost: float
    roof_area_sqm: float
    business_type: str


@dataclass
class SolarAnalysisResult:
    """Model 1 output - Sunshine Checker"""
    solar_irradiance_kwh_m2_day: float
    annual_sunshine_hours: float
    optimal_panel_angle: float
    shading_factor: float
    solar_potential_score: float  # 0-10
    model_confidence: float  # 0-100


@dataclass
class CostAnalysisResult:
    """Model 2 output - Cost Checker"""
    system_size_kw: float
    installation_cost: float
    annual_energy_production_kwh: float
    annual_savings: float
    roi_years: float
    payback_period_years: float
    net_present_value: float
    incentives_available: float


@dataclass
class BusinessSuitabilityResult:
    """Model 3 output - Business Fit Checker"""
    business_hours_match_score: float  # 0-10
    energy_pattern_compatibility: float  # 0-10
    roof_suitability_score: float  # 0-10
    maintenance_capacity_score: float  # 0-10
    overall_suitability_score: float  # 0-10
    risk_factors: List[str]
    opportunities: List[str]


@dataclass
class FinalRecommendation:
    """Final output - What we tell the user"""
    solar_viable: bool
    recommended_system_size_kw: float
    estimated_roi_years: float
    confidence_score: float
    recommendation_summary: str
    key_reasons: List[str]
    warnings: List[str]
    next_steps: List[str]


# ============================================
# MODEL CLIENTS (Talk to the 3 AI models)
# ============================================

class Model1SolarClient:
    """Calls Model 1 - Solar Irradiance Analysis"""
    
    async def analyze(self, business: BusinessInput) -> SolarAnalysisResult:
        """
        Calls Model 1 API and returns solar potential
        In production: Replace with actual API call
        """
        logger.info(f"🌞 Calling Model 1 for {business.business_name}")
        
        # TODO: Replace with actual API call
        # response = await http_client.post(
        #     "https://model1-api.example.com/analyze",
        #     json={"lat": business.latitude, "lon": business.longitude}
        # )
        
        # For now: Return mock data
        await asyncio.sleep(0.5)  # Simulate API delay
        
        return SolarAnalysisResult(
            solar_irradiance_kwh_m2_day=5.8,  # High for Nairobi
            annual_sunshine_hours=2800,
            optimal_panel_angle=15.0,
            shading_factor=0.85,  # 85% unshaded
            solar_potential_score=8.5,
            model_confidence=92.0
        )


class Model2CostClient:
    """Calls Model 2 - Cost & ROI Analysis"""
    
    async def analyze(
        self, 
        business: BusinessInput,
        solar_data: SolarAnalysisResult
    ) -> CostAnalysisResult:
        """
        Calls Model 2 API and returns cost analysis
        Uses solar data from Model 1
        """
        logger.info(f"💰 Calling Model 2 for {business.business_name}")
        
        # TODO: Replace with actual API call
        await asyncio.sleep(0.5)
        
        # Simple calculation for demo
        system_size = business.roof_area_sqm * 0.15  # ~150W per sqm
        installation_cost = system_size * 80000  # KES per kW
        annual_production = system_size * solar_data.solar_irradiance_kwh_m2_day * 365
        annual_savings = min(annual_production, business.monthly_energy_usage_kwh * 12) * 12  # KES/kWh
        
        return CostAnalysisResult(
            system_size_kw=system_size,
            installation_cost=installation_cost,
            annual_energy_production_kwh=annual_production,
            annual_savings=annual_savings,
            roi_years=installation_cost / annual_savings if annual_savings > 0 else 999,
            payback_period_years=4.2,
            net_present_value=installation_cost * 1.5,
            incentives_available=installation_cost * 0.2
        )


class Model3BusinessClient:
    """Calls Model 3 - Business Suitability Analysis"""
    
    async def analyze(
        self,
        business: BusinessInput,
        solar_data: SolarAnalysisResult,
        cost_data: CostAnalysisResult
    ) -> BusinessSuitabilityResult:
        """
        Calls Model 3 API and returns business fit score
        Uses data from Models 1 & 2
        """
        logger.info(f"🏢 Calling Model 3 for {business.business_name}")
        
        # TODO: Replace with actual API call
        await asyncio.sleep(0.5)
        
        return BusinessSuitabilityResult(
            business_hours_match_score=9.0,  # Coffee shop = daytime
            energy_pattern_compatibility=8.5,
            roof_suitability_score=7.5,
            maintenance_capacity_score=6.0,
            overall_suitability_score=7.8,
            risk_factors=[
                "Limited maintenance capacity for small business",
                "Roof may require structural assessment"
            ],
            opportunities=[
                "Peak energy use aligns with solar production",
                "Can reduce grid dependency during outages",
                "Positive environmental branding opportunity"
            ]
        )


# ============================================
# DECISION ENGINE (Your Rules)
# ============================================

class DecisionEngine:
    """
    Applies business rules to decide if solar is viable
    This is YOUR logic - the brain's thinking
    """
    
    # Thresholds (adjust these!)
    MIN_SOLAR_SCORE = 6.0
    MAX_ROI_YEARS = 7.0
    MIN_SUITABILITY_SCORE = 6.0
    MIN_CONFIDENCE = 70.0
    
    @classmethod
    def make_decision(
        cls,
        solar: SolarAnalysisResult,
        cost: CostAnalysisResult,
        suitability: BusinessSuitabilityResult,
        business: BusinessInput
    ) -> FinalRecommendation:
        """
        The MAIN decision logic
        This is where you say YES or NO
        """
        logger.info("🧠 Making final decision...")
        
        # ========================================
        # STEP 1: Check each criteria
        # ========================================
        
        criteria_checks = {
            "solar_score": solar.solar_potential_score >= cls.MIN_SOLAR_SCORE,
            "roi": cost.roi_years <= cls.MAX_ROI_YEARS,
            "suitability": suitability.overall_suitability_score >= cls.MIN_SUITABILITY_SCORE,
            "confidence": solar.model_confidence >= cls.MIN_CONFIDENCE
        }
        
        # ========================================
        # STEP 2: Calculate confidence
        # ========================================
        
        confidence_factors = [
            solar.model_confidence,
            min(100, (10 - cost.roi_years) * 10),  # Lower ROI = higher confidence
            suitability.overall_suitability_score * 10
        ]
        confidence_score = sum(confidence_factors) / len(confidence_factors)
        
        # ========================================
        # STEP 3: Make YES/NO decision
        # ========================================
        
        viable = all(criteria_checks.values())
        
        # ========================================
        # STEP 4: Build explanation
        # ========================================
        
        reasons = []
        warnings = []
        
        if criteria_checks["solar_score"]:
            reasons.append(
                f"Excellent solar potential (score: {solar.solar_potential_score}/10) "
                f"with {solar.annual_sunshine_hours} sunshine hours/year"
            )
        else:
            warnings.append(
                f"Low solar potential (score: {solar.solar_potential_score}/10)"
            )
        
        if criteria_checks["roi"]:
            reasons.append(
                f"Strong ROI of {cost.roi_years:.1f} years "
                f"with annual savings of KES {cost.annual_savings:,.0f}"
            )
        else:
            warnings.append(
                f"ROI of {cost.roi_years:.1f} years exceeds {cls.MAX_ROI_YEARS} year threshold"
            )
        
        if criteria_checks["suitability"]:
            reasons.append(
                f"Business operations well-suited for solar "
                f"(suitability score: {suitability.overall_suitability_score}/10)"
            )
        else:
            warnings.append(
                f"Business suitability concerns (score: {suitability.overall_suitability_score}/10)"
            )
        
        # Add risk factors as warnings
        warnings.extend(suitability.risk_factors)
        
        # ========================================
        # STEP 5: Create summary
        # ========================================
        
        if viable:
            summary = (
                f"Solar installation is RECOMMENDED for {business.business_name}. "
                f"A {cost.system_size_kw:.1f}kW system would provide strong returns "
                f"with ROI in {cost.roi_years:.1f} years and annual savings of "
                f"KES {cost.annual_savings:,.0f}."
            )
        else:
            summary = (
                f"Solar installation is NOT RECOMMENDED for {business.business_name} "
                f"at this time. Key concerns: {', '.join(warnings[:2])}."
            )
        
        # ========================================
        # STEP 6: Next steps
        # ========================================
        
        if viable:
            next_steps = [
                "Schedule roof structural assessment",
                "Obtain detailed quotes from 3+ solar installers",
                "Apply for available government incentives",
                "Review and compare financing options",
                "Plan installation timeline to minimize business disruption"
            ]
        else:
            next_steps = [
                "Monitor energy costs - reassess if electricity prices increase",
                "Consider energy efficiency improvements first",
                "Explore alternative renewable options (e.g., solar water heating)",
                "Revisit analysis in 12-18 months"
            ]
        
        return FinalRecommendation(
            solar_viable=viable,
            recommended_system_size_kw=cost.system_size_kw,
            estimated_roi_years=cost.roi_years,
            confidence_score=confidence_score,
            recommendation_summary=summary,
            key_reasons=reasons,
            warnings=warnings,
            next_steps=next_steps
        )


# ============================================
# ORCHESTRATION SERVICE (The Main Brain)
# ============================================

class SolarViabilityOrchestrator:
    """
    The MAIN CLASS that runs everything
    This is what your API endpoint calls
    """
    
    def __init__(self):
        self.model1 = Model1SolarClient()
        self.model2 = Model2CostClient()
        self.model3 = Model3BusinessClient()
        self.decision_engine = DecisionEngine()
    
    async def analyze_solar_viability(
        self, 
        business: BusinessInput
    ) -> FinalRecommendation:
        """
        MAIN ORCHESTRATION METHOD
        This is the whole workflow in one function
        """
        
        logger.info(f"🚀 Starting solar analysis for {business.business_name}")
        
        try:
            # ========================================
            # STEP 1: Call Model 1 (Solar potential)
            # ========================================
            solar_result = await self.model1.analyze(business)
            logger.info(f"✅ Model 1 complete: Solar score = {solar_result.solar_potential_score}/10")
            
            # ========================================
            # STEP 2: Call Model 2 (Cost & ROI)
            # ========================================
            cost_result = await self.model2.analyze(business, solar_result)
            logger.info(f"✅ Model 2 complete: ROI = {cost_result.roi_years:.1f} years")
            
            # ========================================
            # STEP 3: Call Model 3 (Business fit)
            # ========================================
            suitability_result = await self.model3.analyze(
                business, solar_result, cost_result
            )
            logger.info(f"✅ Model 3 complete: Suitability = {suitability_result.overall_suitability_score}/10")
            
            # ========================================
            # STEP 4: Make final decision
            # ========================================
            recommendation = self.decision_engine.make_decision(
                solar_result,
                cost_result,
                suitability_result,
                business
            )
            
            logger.info(
                f"🎯 Final decision: {'VIABLE' if recommendation.solar_viable else 'NOT VIABLE'} "
                f"(confidence: {recommendation.confidence_score:.1f}%)"
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error during analysis: {str(e)}")
            raise


# ============================================
# CONVENIENCE FUNCTION (Easy to use)
# ============================================

async def analyze_business_for_solar(
    business_name: str,
    location: str,
    latitude: float,
    longitude: float,
    monthly_energy_usage_kwh: float,
    monthly_energy_cost: float,
    roof_area_sqm: float,
    business_type: str
) -> Dict:
    """
    Convenience function that returns a simple dict
    Perfect for API endpoints
    """
    
    # Create business input
    business = BusinessInput(
        business_name=business_name,
        location=location,
        latitude=latitude,
        longitude=longitude,
        monthly_energy_usage_kwh=monthly_energy_usage_kwh,
        monthly_energy_cost=monthly_energy_cost,
        roof_area_sqm=roof_area_sqm,
        business_type=business_type
    )
    
    # Run orchestration
    orchestrator = SolarViabilityOrchestrator()
    recommendation = await orchestrator.analyze_solar_viability(business)
    
    # Convert to dict for JSON response
    return {
        "solar_viable": recommendation.solar_viable,
        "recommended_system_size_kw": recommendation.recommended_system_size_kw,
        "estimated_roi_years": recommendation.estimated_roi_years,
        "confidence_score": recommendation.confidence_score,
        "recommendation_summary": recommendation.recommendation_summary,
        "key_reasons": recommendation.key_reasons,
        "warnings": recommendation.warnings,
        "next_steps": recommendation.next_steps,
        "analyzed_at": datetime.utcnow().isoformat()
    }


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Test with Joe's Coffee Shop
    async def test():
        result = await analyze_business_for_solar(
            business_name="Joe's Coffee Shop",
            location="Nairobi, Kenya",
            latitude=-1.2921,
            longitude=36.8219,
            monthly_energy_usage_kwh=2500,
            monthly_energy_cost=45000,
            roof_area_sqm=150,
            business_type="Food & Beverage"
        )
        
        print("\n" + "="*60)
        print("SOLAR VIABILITY ANALYSIS RESULT")
        print("="*60)
        print(f"\n✅ Viable: {result['solar_viable']}")
        print(f"📊 System Size: {result['recommended_system_size_kw']:.1f} kW")
        print(f"💰 ROI: {result['estimated_roi_years']:.1f} years")
        print(f"🎯 Confidence: {result['confidence_score']:.1f}%")
        print(f"\n📝 Summary:\n{result['recommendation_summary']}")
        print(f"\n✨ Key Reasons:")
        for reason in result['key_reasons']:
            print(f"  • {reason}")
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"  • {warning}")
        print(f"\n📋 Next Steps:")
        for i, step in enumerate(result['next_steps'], 1):
            print(f"  {i}. {step}")
        print("\n" + "="*60 + "\n")
    
    asyncio.run(test())
