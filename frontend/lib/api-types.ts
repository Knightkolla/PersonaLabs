// TypeScript types matching backend Pydantic models

export enum BusinessModel {
    B2B = "B2B",
    B2C = "B2C",
    B2B2C = "B2B2C",
    MARKETPLACE = "Marketplace",
    SAAS = "SaaS",
    OTHER = "Other"
}

export enum CompanySize {
    STARTUP = "Startup",
    SMB = "SMB",
    MID_MARKET = "Mid-Market",
    ENTERPRISE = "Enterprise"
}

export enum ImplementationComplexity {
    LOW = "Low",
    MEDIUM = "Medium",
    HIGH = "High"
}

export enum TechnologyAdoption {
    INNOVATOR = "Innovator",
    EARLY_ADOPTER = "Early Adopter",
    EARLY_MAJORITY = "Early Majority",
    LATE_MAJORITY = "Late Majority",
    LAGGARD = "Laggard"
}

export enum SimulationDecision {
    ADOPT = "ADOPT",
    REJECT = "REJECT",
    UNSURE = "UNSURE"
}

export interface CompanyInput {
    name: string;
    industry: string;
    target_market: string;
    business_model: BusinessModel;
    company_size: CompanySize;
    description: string;
}

export interface FeatureDescription {
    name: string;
    description: string;
    value_proposition: string;
    target_user: string;
    pricing_model: string;
    implementation_complexity?: ImplementationComplexity;
    competitor_comparison?: string;
}

export interface Demographics {
    age: number;
    role: string;
    company_size: string;
    industry: string;
    income: string;
}

export interface Psychographics {
    personality_traits: string[];
    values: string[];
    motivations: string[];
    pain_points: string[];
}

export interface BehaviorPatterns {
    technology_adoption: TechnologyAdoption;
    decision_making_style: string;
    risk_tolerance: string;
    information_sources: string[];
}

export interface ContextualFactors {
    current_solutions: string[];
    budget: string;
    time_constraints: string;
    team_influence: string;
}

export interface SyntheticPersona {
    id: string;
    name: string;
    demographics: Demographics;
    psychographics: Psychographics;
    behavior_patterns: BehaviorPatterns;
    contextual_factors: ContextualFactors;
}

export interface CompanyContext {
    id: string;
    input: CompanyInput;
    enriched_context: Record<string, any>;
    persona_seeds: Record<string, any>[];
}

export interface SimulationResponse {
    persona_id: string;
    decision: SimulationDecision;
    confidence: number;
    reasoning: string;
    key_factors: string[];
    timestamp: string;
    model_used: string;
}

export interface ObjectionCluster {
    objection: string;
    frequency: number;
    affected_personas: string[];
}

export interface SuccessFactor {
    factor: string;
    importance: number;
    supporting_personas: string[];
}

export interface Recommendations {
    messaging: string[];
    target_segments: string[];
    feature_improvements: string[];
}

export interface ReasoningPattern {
    pattern_type: "theme" | "objection_cluster" | "success_driver";
    description: string;
    frequency: number;
    example_quotes: string[];
    affected_personas: string[];
}

export interface AggregatedInsights {
    overall_adoption_rate: number;
    confidence_interval: [number, number];
    adoption_by_segment: Record<string, number>;
    top_objections: ObjectionCluster[];
    key_success_factors: SuccessFactor[];
    recommendations: Recommendations;
    reasoning_patterns?: ReasoningPattern[];
}

export interface Experiment {
    id: string;
    user_id?: string;
    created_at: string;
    updated_at: string;
    company_context: CompanyContext;
    feature_description: FeatureDescription;
    personas: SyntheticPersona[];
    simulation_results: SimulationResponse[];
    aggregated_insights?: AggregatedInsights;
    is_public: boolean;
    share_token?: string;
}

export interface ExperimentResponse {
    experiment: Experiment;
    status: string;
    message?: string;
}

export interface CreateExperimentRequest {
    company_input: CompanyInput;
    feature_description: FeatureDescription;
}
