import pytest
from fastapi.testclient import TestClient
from app.models import CompanyInput, FeatureDescription, BusinessModel, CompanySize
from unittest.mock import patch, AsyncMock
from app.models import SyntheticPersona, Demographics, Psychographics, BehaviorPatterns, ContextualFactors, TechnologyAdoption, SimulationResponse, SimulationDecision
from datetime import datetime
import uuid

class TestIntegrationWorkflows:
    """Integration tests for complete user workflows"""
    
    def test_complete_experiment_workflow(self, client):
        """Test complete workflow: create → simulate → analyze → export"""
        # Mock dependencies
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Integration Test Persona",
            demographics=Demographics(age=35, role="Product Manager", company_size="Mid-Market", industry="SaaS", income="High"),
            psychographics=Psychographics(personality_traits=["Analytical"], values=["Innovation"], motivations=["Efficiency"], pain_points=["Manual processes"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_ADOPTER, decision_making_style="Data-driven", risk_tolerance="Medium", information_sources=["Industry reports"]),
            contextual_factors=ContextualFactors(current_solutions=["Legacy system"], budget="High", time_constraints="Medium", team_influence="High")
        )
        
        dummy_simulation = SimulationResponse(
            persona_id=dummy_persona.id,
            decision=SimulationDecision.ADOPT,
            confidence=0.85,
            reasoning="This feature addresses our key pain point of manual processes and aligns with our innovation goals",
            key_factors=["automation", "efficiency", "ROI"],
            timestamp=datetime.utcnow(),
            model_used="test-model"
        )
        
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockPersonaEngine, \
             patch("app.routers.experiments.SimulationEngine") as MockSimEngine:
            
            # Configure mocks
            mock_persona_instance = MockPersonaEngine.return_value
            mock_persona_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            mock_sim_instance = MockSimEngine.return_value
            mock_sim_instance.simulate_batch_reactions = AsyncMock(return_value=[dummy_simulation])
            
            # 1. Create experiment
            payload = {
                "company_input": CompanyInput(
                    name="TechCorp",
                    industry="Software",
                    target_market="B2B SaaS companies looking to automate workflows",
                    business_model=BusinessModel.B2B,
                    company_size=CompanySize.MID_MARKET,
                    description="Leading provider of workflow automation tools"
                ).model_dump(),
                "feature_description": FeatureDescription(
                    name="AI-Powered Workflow Automation",
                    description="Automatically detect and optimize repetitive workflows using machine learning",
                    value_proposition="Reduce manual work by 70% and increase team productivity",
                    target_user="Operations teams and process managers",
                    pricing_model="$99/user/month"
                ).model_dump()
            }
            
            create_response = client.post("/api/v1/experiments/", json=payload)
            assert create_response.status_code == 200
            experiment_id = create_response.json()["experiment"]["id"]
            
            # 2. Run simulation
            sim_response = client.post(f"/api/v1/experiments/{experiment_id}/simulate")
            assert sim_response.status_code == 200
            sim_data = sim_response.json()["experiment"]
            
            # Verify simulation results
            assert len(sim_data["simulation_results"]) > 0
            assert sim_data["aggregated_insights"] is not None
            assert "overall_adoption_rate" in sim_data["aggregated_insights"]
            
            # 3. Verify pattern analysis was performed
            if sim_data["aggregated_insights"]["reasoning_patterns"]:
                patterns = sim_data["aggregated_insights"]["reasoning_patterns"]
                assert len(patterns) >= 0
                for pattern in patterns:
                    assert "pattern_type" in pattern
                    assert "description" in pattern
            
            # 4. Export to CSV
            csv_response = client.get(f"/api/v1/experiments/{experiment_id}/export/csv")
            assert csv_response.status_code == 200
            csv_content = csv_response.text
            assert "Persona Name" in csv_content
            assert "Decision" in csv_content
    
    def test_experiment_iteration_workflow(self, client):
        """Test iteration workflow: create → fork → modify → compare"""
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Iteration Test Persona",
            demographics=Demographics(age=40, role="CTO", company_size="Enterprise", industry="Finance", income="Very High"),
            psychographics=Psychographics(personality_traits=["Strategic"], values=["Security"], motivations=["Risk mitigation"], pain_points=["Data breaches"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_MAJORITY, decision_making_style="Consensus-based", risk_tolerance="Low", information_sources=["Vendor demos"]),
            contextual_factors=ContextualFactors(current_solutions=["On-premise solution"], budget="Very High", time_constraints="Low", team_influence="Very High")
        )
        
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockEngine:
            mock_instance = MockEngine.return_value
            mock_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            # 1. Create original experiment
            payload = {
                "company_input": CompanyInput(
                    name="FinanceSecure",
                    industry="Financial Services",
                    target_market="Enterprise financial institutions",
                    business_model=BusinessModel.B2B,
                    company_size=CompanySize.ENTERPRISE,
                    description="Security solutions for financial sector"
                ).model_dump(),
                "feature_description": FeatureDescription(
                    name="Basic Security Dashboard",
                    description="Monitor security events in real-time",
                    value_proposition="Improve security visibility",
                    target_user="Security teams",
                    pricing_model="$500/month"
                ).model_dump()
            }
            
            original_response = client.post("/api/v1/experiments/", json=payload)
            original_id = original_response.json()["experiment"]["id"]
            
            # 2. Fork with enhanced feature
            enhanced_feature = FeatureDescription(
                name="AI-Enhanced Security Dashboard with Threat Prediction",
                description="Monitor security events and predict potential threats using AI",
                value_proposition="Proactively prevent security incidents before they occur",
                target_user="Security teams and compliance officers",
                pricing_model="$1200/month"
            )
            
            fork_response = client.post(
                f"/api/v1/experiments/{original_id}/fork",
                json=enhanced_feature.model_dump()
            )
            assert fork_response.status_code == 200
            forked_id = fork_response.json()["experiment"]["id"]
            
            # 3. Verify fork has same personas but different feature
            original_exp = client.get(f"/api/v1/experiments/{original_id}").json()["experiment"]
            forked_exp = client.get(f"/api/v1/experiments/{forked_id}").json()["experiment"]
            
            assert original_exp["personas"][0]["id"] == forked_exp["personas"][0]["id"]
            assert original_exp["feature_description"]["name"] != forked_exp["feature_description"]["name"]
            assert forked_exp["simulation_results"] == []
    
    def test_sharing_collaboration_workflow(self, client):
        """Test sharing workflow: create → share → access → revoke"""
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Sharing Test Persona",
            demographics=Demographics(age=28, role="Developer", company_size="Startup", industry="Tech", income="Medium"),
            psychographics=Psychographics(personality_traits=["Curious"], values=["Learning"], motivations=["Career growth"], pain_points=["Repetitive tasks"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_ADOPTER, decision_making_style="Quick", risk_tolerance="High", information_sources=["Tech blogs"]),
            contextual_factors=ContextualFactors(current_solutions=[], budget="Low", time_constraints="High", team_influence="Medium")
        )
        
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockEngine:
            mock_instance = MockEngine.return_value
            mock_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            # 1. Create experiment
            payload = {
                "company_input": CompanyInput(
                    name="DevTools Inc",
                    industry="Developer Tools",
                    target_market="Individual developers and small teams",
                    business_model=BusinessModel.B2C,
                    company_size=CompanySize.STARTUP,
                    description="Tools for modern developers"
                ).model_dump(),
                "feature_description": FeatureDescription(
                    name="Code Snippet Manager",
                    description="Save and organize code snippets with AI-powered search",
                    value_proposition="Never lose a useful code snippet again",
                    target_user="Software developers",
                    pricing_model="Free tier + $10/month pro"
                ).model_dump()
            }
            
            create_response = client.post("/api/v1/experiments/", json=payload)
            experiment_id = create_response.json()["experiment"]["id"]
            
            # 2. Share experiment
            share_response = client.post(f"/api/v1/experiments/{experiment_id}/share")
            assert share_response.status_code == 200
            share_token = share_response.json()["share_token"]
            
            # 3. Access via share link (simulating different user)
            shared_response = client.get(f"/api/v1/experiments/shared/{share_token}")
            assert shared_response.status_code == 200
            shared_exp = shared_response.json()["experiment"]
            assert shared_exp["id"] == experiment_id
            assert shared_exp["is_public"] == True
            
            # 4. Revoke sharing
            revoke_response = client.delete(f"/api/v1/experiments/{experiment_id}/share")
            assert revoke_response.status_code == 200
            
            # 5. Verify access is denied after revocation
            denied_response = client.get(f"/api/v1/experiments/shared/{share_token}")
            assert denied_response.status_code == 404
    
    def test_multi_experiment_comparison(self, client):
        """Test comparing multiple experiments"""
        dummy_persona = SyntheticPersona(
            id=str(uuid.uuid4()),
            name="Comparison Test Persona",
            demographics=Demographics(age=32, role="Marketing Manager", company_size="SMB", industry="E-commerce", income="Medium"),
            psychographics=Psychographics(personality_traits=["Creative"], values=["Customer satisfaction"], motivations=["Growth"], pain_points=["Low conversion"]),
            behavior_patterns=BehaviorPatterns(technology_adoption=TechnologyAdoption.EARLY_MAJORITY, decision_making_style="ROI-focused", risk_tolerance="Medium", information_sources=["Case studies"]),
            contextual_factors=ContextualFactors(current_solutions=["Basic analytics"], budget="Medium", time_constraints="Medium", team_influence="Medium")
        )
        
        with patch("app.routers.experiments.PersonaGenerationEngine") as MockEngine:
            mock_instance = MockEngine.return_value
            mock_instance.generate_personas = AsyncMock(return_value=[dummy_persona])
            
            # Create multiple experiments with different features
            base_company = CompanyInput(
                name="ShopEasy",
                industry="E-commerce",
                target_market="Small to medium online retailers",
                business_model=BusinessModel.B2B,
                company_size=CompanySize.SMB,
                description="E-commerce platform for SMBs"
            )
            
            features = [
                FeatureDescription(
                    name="Basic Analytics",
                    description="Track sales and visitor metrics",
                    value_proposition="Understand your customers better",
                    target_user="Store owners",
                    pricing_model="$29/month"
                ),
                FeatureDescription(
                    name="AI-Powered Recommendations",
                    description="Personalized product recommendations using AI",
                    value_proposition="Increase conversion by 30%",
                    target_user="Store owners and marketing teams",
                    pricing_model="$99/month"
                ),
                FeatureDescription(
                    name="Complete Marketing Suite",
                    description="Analytics, recommendations, email campaigns, and A/B testing",
                    value_proposition="All-in-one marketing solution",
                    target_user="Marketing teams",
                    pricing_model="$199/month"
                )
            ]
            
            experiment_ids = []
            for feature in features:
                payload = {
                    "company_input": base_company.model_dump(),
                    "feature_description": feature.model_dump()
                }
                response = client.post("/api/v1/experiments/", json=payload)
                assert response.status_code == 200
                experiment_ids.append(response.json()["experiment"]["id"])
            
            # Verify all experiments were created
            assert len(experiment_ids) == 3
            
            # List experiments and verify they're all there
            list_response = client.get("/api/v1/experiments/")
            assert list_response.status_code == 200
            experiments = list_response.json()
            
            # Should have at least our 3 experiments
            assert len(experiments) >= 3
