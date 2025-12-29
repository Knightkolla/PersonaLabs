
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from app.models import CompanyInput, FeatureDescription, BusinessModel, CompanySize, ImplementationComplexity
import uuid

# Strategies for request models
def company_input_strategy():
    return st.builds(
        CompanyInput,
        name=st.text(min_size=1, max_size=50),
        industry=st.text(min_size=1, max_size=50),
        target_market=st.text(min_size=1, max_size=50),
        business_model=st.sampled_from(list(BusinessModel)),
        company_size=st.sampled_from(list(CompanySize)),
        description=st.text(min_size=0, max_size=100)
    )

def feature_description_strategy():
    return st.builds(
        FeatureDescription,
        name=st.text(min_size=1, max_size=50),
        description=st.text(min_size=1, max_size=200),
        value_proposition=st.text(min_size=1, max_size=50),
        target_user=st.text(min_size=1, max_size=50),
        pricing_model=st.text(min_size=1, max_size=50),
        implementation_complexity=st.sampled_from(list(ImplementationComplexity)),
        competitor_comparison=st.text(min_size=0, max_size=50)
    )

class TestPropertyExperimentManagement:
    
    @settings(max_examples=10, deadline=None)
    @given(company_input=company_input_strategy(), feature_description=feature_description_strategy())
    def test_experiment_persistence(self, client, company_input, feature_description):
        """Property 27: Experiment persistence capability"""
        from unittest.mock import patch, AsyncMock
        from app.models import SyntheticPersona, Demographics, Psychographics, BehaviorPatterns, ContextualFactors, TechnologyAdoption
        
        # Create a dummy persona
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Test Persona",
            demographics=Demographics(age=30, role="Tester", company_size="Small", industry="Tech", income="High"),
            psychographics=Psychographics(personality_traits=["Test"], values=["Test"], motivations=["Test"], pain_points=["Test"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_ADOPTER, decision_making_style="Fast", risk_tolerance="High", information_sources=["Test"]),
            contextual_factors=ContextualFactors(current_solutions=[], budget="High", time_constraints="Low", team_influence="High")
        )
        
        # Patch the engine in the router module
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockEngine:
            # Configure the mock instance
            mock_instance = MockEngine.return_value
            # Configure the async method
            mock_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            # 1. Create Experiment
            payload = {
                "company_input": company_input.model_dump(),
                "feature_description": feature_description.model_dump()
            }
            
            response = client.post("/api/v1/experiments/", json=payload)
            assert response.status_code == 200
            created_data = response.json()
            experiment_id = created_data["experiment"]["id"]
            
            # 2. Retrieve Experiment
            get_response = client.get(f"/api/v1/experiments/{experiment_id}")
            assert get_response.status_code == 200
            retrieved_data = get_response.json()
            
            # 3. Verify Fields
            assert retrieved_data["experiment"]["id"] == experiment_id
            # Check serialized fields match inputs
            retrieved_feature = retrieved_data["experiment"]["feature_description"]
            assert retrieved_feature["name"] == feature_description.name
            
            # Check personas were generated (mocked logic)
            assert len(retrieved_data["experiment"]["personas"]) == 1
            assert retrieved_data["experiment"]["personas"][0]["name"] == "Test Persona"

    @settings(max_examples=10, deadline=None)
    @given(company_input=company_input_strategy(), 
           feature_1=feature_description_strategy(), 
           feature_2=feature_description_strategy())
    def test_experiment_forking(self, client, company_input, feature_1, feature_2):
        """Property 28: Iteration functionality preservation"""
        from unittest.mock import patch, AsyncMock
        from app.models import SyntheticPersona, Demographics, Psychographics, BehaviorPatterns, ContextualFactors, TechnologyAdoption
        
        # Create a dummy persona
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Test Persona",
            demographics=Demographics(age=30, role="Tester", company_size="Small", industry="Tech", income="High"),
            psychographics=Psychographics(personality_traits=["Test"], values=["Test"], motivations=["Test"], pain_points=["Test"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_ADOPTER, decision_making_style="Fast", risk_tolerance="High", information_sources=["Test"]),
            contextual_factors=ContextualFactors(current_solutions=[], budget="High", time_constraints="Low", team_influence="High")
        )
        
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockEngine:
            mock_instance = MockEngine.return_value
            mock_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            # 1. Create initial experiment
            payload = {
                "company_input": company_input.model_dump(),
                "feature_description": feature_1.model_dump()
            }
            response = client.post("/api/v1/experiments/", json=payload)
            assert response.status_code == 200
            original_exp = response.json()["experiment"]
            original_id = original_exp["id"]
            original_personas = original_exp["personas"]
            
            # 2. Fork experiment
            fork_response = client.post(
                f"/api/v1/experiments/{original_id}/fork",
                json=feature_2.model_dump()
            )
            assert fork_response.status_code == 200
            forked_exp = fork_response.json()["experiment"]
            
            # 3. Verify Logic
            # New ID
            assert forked_exp["id"] != original_id
            # Same Personas
            assert len(forked_exp["personas"]) == len(original_personas)
            assert forked_exp["personas"][0]["name"] == original_personas[0]["name"]
            # New Feature
            assert forked_exp["feature_description"]["name"] == feature_2.name
            # Results Reset
            assert forked_exp["simulation_results"] == []
