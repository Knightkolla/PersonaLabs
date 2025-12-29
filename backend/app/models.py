from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums
class BusinessModel(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    B2B2C = "B2B2C"
    MARKETPLACE = "Marketplace"

class CompanySize(str, Enum):
    STARTUP = "Startup"
    SMB = "SMB"
    MID_MARKET = "Mid-Market"
    ENTERPRISE = "Enterprise"

class TechnologyAdoption(str, Enum):
    EARLY_ADOPTER = "Early Adopter"
    EARLY_MAJORITY = "Early Majority"
    LATE_MAJORITY = "Late Majority"
    LAGGARD = "Laggard"

class RiskTolerance(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ImplementationComplexity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class SimulationDecision(str, Enum):
    ADOPT = "ADOPT"
    REJECT = "REJECT"
    UNSURE = "UNSURE"

# Input Models
class CompanyInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    business_model: BusinessModel
    target_market: str = Field(..., min_length=1, max_length=500)
    company_size: CompanySize
    description: Optional[str] = Field(None, max_length=1000)

class FeatureDescription(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    target_user: str = Field(..., min_length=1, max_length=200)
    value_proposition: str = Field(..., min_length=1, max_length=500)
    pricing_model: Optional[str] = Field(None, max_length=200)
    implementation_complexity: Optional[ImplementationComplexity] = None
    competitor_comparison: Optional[str] = Field(None, max_length=500)

# Core Data Models
class Demographics(BaseModel):
    age: int = Field(..., ge=18, le=100)
    role: str = Field(..., min_length=1, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    income: Optional[str] = Field(None, max_length=50)

class Psychographics(BaseModel):
    personality_traits: List[str] = Field(..., min_length=1, max_length=10)
    values: List[str] = Field(..., min_length=1, max_length=10)
    motivations: List[str] = Field(..., min_length=1, max_length=10)
    pain_points: List[str] = Field(..., min_length=1, max_length=10)

class BehaviorPatterns(BaseModel):
    technology_adoption: TechnologyAdoption
    decision_making_style: str = Field(..., min_length=1, max_length=200)
    risk_tolerance: RiskTolerance
    information_sources: List[str] = Field(..., min_length=1, max_length=10)

class ContextualFactors(BaseModel):
    current_solutions: List[str] = Field(..., min_length=0, max_length=10)
    budget: str = Field(..., min_length=1, max_length=100)
    time_constraints: str = Field(..., min_length=1, max_length=200)
    team_influence: str = Field(..., min_length=1, max_length=200)

class SyntheticPersona(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    demographics: Demographics
    psychographics: Psychographics
    behavior_patterns: BehaviorPatterns
    contextual_factors: ContextualFactors

class SimulationResponse(BaseModel):
    persona_id: str = Field(..., min_length=1)
    decision: SimulationDecision
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=1, max_length=1000)
    key_factors: List[str] = Field(..., min_length=1, max_length=5)
    timestamp: datetime
    model_used: str = Field(..., min_length=1, max_length=50)

class CompanyContext(BaseModel):
    id: str = Field(..., min_length=1)
    input: CompanyInput
    enriched_context: Dict[str, Any]
    persona_seeds: List[Dict[str, Any]]

class ObjectionCluster(BaseModel):
    objection: str = Field(..., min_length=1, max_length=500)
    frequency: int = Field(..., ge=0)
    affected_personas: List[str] = Field(..., min_length=0)

class SuccessFactor(BaseModel):
    factor: str = Field(..., min_length=1, max_length=500)
    importance: float = Field(..., ge=0.0, le=1.0)
    supporting_personas: List[str] = Field(..., min_length=0)

class Recommendations(BaseModel):
    messaging: List[str] = Field(..., min_length=0, max_length=10)
    target_segments: List[str] = Field(..., min_length=0, max_length=10)
    feature_improvements: List[str] = Field(..., min_length=0, max_length=10)

class ReasoningPattern(BaseModel):
    """Represents a pattern found in persona reasoning"""
    pattern_type: Literal["theme", "objection_cluster", "success_driver"]
    description: str = Field(..., min_length=1, max_length=500)
    frequency: int = Field(..., ge=1)
    example_quotes: List[str] = Field(..., min_length=1, max_length=5)
    affected_personas: List[str] = Field(..., min_length=1)

class AggregatedInsights(BaseModel):
    overall_adoption_rate: float = Field(..., ge=0.0, le=1.0)
    confidence_interval: tuple[float, float]
    adoption_by_segment: Dict[str, float]
    top_objections: List[ObjectionCluster]
    key_success_factors: List[SuccessFactor]
    recommendations: Recommendations
    reasoning_patterns: Optional[List[ReasoningPattern]] = None

class Experiment(BaseModel):
    id: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    company_context: CompanyContext
    feature_description: FeatureDescription
    personas: List[SyntheticPersona]
    simulation_results: List[SimulationResponse]
    aggregated_insights: Optional[AggregatedInsights] = None
    is_public: bool = False
    share_token: Optional[str] = None

# Request/Response Models
class CreateExperimentRequest(BaseModel):
    company_input: CompanyInput
    feature_description: FeatureDescription

class ExperimentResponse(BaseModel):
    experiment: Experiment
    status: str
    message: Optional[str] = None