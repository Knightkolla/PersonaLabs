import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from fastapi.testclient import TestClient
from app.models import CompanyInput, FeatureDescription, BusinessModel, CompanySize, ImplementationComplexity
import uuid

# Strategies (reuse from experiment management tests)
def company_input_strategy():
    return st.builds(
        CompanyInput,
        name=st.text(min_size=5, max_size=50),
        industry=st.text(min_size=5, max_size=50),
        target_market=st.text(min_size=20, max_size=100),
        business_model=st.sampled_from(list(BusinessModel)),
        company_size=st.sampled_from(list(CompanySize)),
        description=st.text(min_size=10, max_size=100)
    )

def feature_description_strategy():
    return st.builds(
        FeatureDescription,
        name=st.text(min_size=5, max_size=50),
        description=st.text(min_size=30, max_size=200),
        value_proposition=st.text(min_size=20, max_size=100),
        target_user=st.text(min_size=5, max_size=50),
        pricing_model=st.text(min_size=5, max_size=50),
        implementation_complexity=st.sampled_from(list(ImplementationComplexity)),
        competitor_comparison=st.text(min_size=0, max_size=50)
    )

class TestPropertySharing:
    
    @settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(company_input=company_input_strategy(), feature_description=feature_description_strategy())
    def test_sharing_workflow(self, client, company_input, feature_description):
        """Property 31: Sharing functionality - share, access, and revoke"""
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
            
            # 1. Create experiment
            payload = {
                "company_input": company_input.model_dump(),
                "feature_description": feature_description.model_dump()
            }
            response = client.post("/api/v1/experiments/", json=payload)
            assert response.status_code == 200
            experiment_id = response.json()["experiment"]["id"]
            
            # 2. Share experiment
            share_response = client.post(f"/api/v1/experiments/{experiment_id}/share")
            assert share_response.status_code == 200
            share_data = share_response.json()
            assert "share_token" in share_data
            assert "share_url" in share_data
            share_token = share_data["share_token"]
            
            # 3. Access shared experiment
            shared_response = client.get(f"/api/v1/experiments/shared/{share_token}")
            assert shared_response.status_code == 200
            shared_exp = shared_response.json()["experiment"]
            assert shared_exp["id"] == experiment_id
            assert shared_exp["is_public"] == True
            
            # 4. Revoke sharing
            revoke_response = client.delete(f"/api/v1/experiments/{experiment_id}/share")
            assert revoke_response.status_code == 200
            
            # 5. Verify access is revoked
            revoked_response = client.get(f"/api/v1/experiments/shared/{share_token}")
            assert revoked_response.status_code == 404
    
    def test_share_token_uniqueness(self, client):
        """Verify that share tokens are unique"""
        from unittest.mock import patch, AsyncMock
        from app.models import SyntheticPersona, Demographics, Psychographics, BehaviorPatterns, ContextualFactors, TechnologyAdoption, CompanyInput, FeatureDescription, BusinessModel, CompanySize
        
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
            
            # Create two experiments
            payload = {
                "company_input": CompanyInput(
                    name="Test Co",
                    industry="Tech",
                    target_market="Developers and tech teams",
                    business_model=BusinessModel.B2B,
                    company_size=CompanySize.STARTUP,
                    description="Test company"
                ).model_dump(),
                "feature_description": FeatureDescription(
                    name="Test Feature",
                    description="A test feature for validation",
                    value_proposition="Saves time and money",
                    target_user="Developers",
                    pricing_model="Free"
                ).model_dump()
            }
            
            response1 = client.post("/api/v1/experiments/", json=payload)
            response2 = client.post("/api/v1/experiments/", json=payload)
            
            exp_id_1 = response1.json()["experiment"]["id"]
            exp_id_2 = response2.json()["experiment"]["id"]
            
            # Share both
            share1 = client.post(f"/api/v1/experiments/{exp_id_1}/share")
            share2 = client.post(f"/api/v1/experiments/{exp_id_2}/share")
            
            token1 = share1.json()["share_token"]
            token2 = share2.json()["share_token"]
            
            # Tokens should be unique
            assert token1 != token2
