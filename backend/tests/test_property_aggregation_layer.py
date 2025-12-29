
import pytest
from hypothesis import given, strategies as st
from app.services.aggregation_layer import AggregationLayer
from app.models import (
    SimulationResponse, SimulationDecision, SyntheticPersona, 
    Demographics, Psychographics, BehaviorPatterns, ContextualFactors,
    TechnologyAdoption, RiskTolerance, CompanySize, Experiment,
    CompanyContext, CompanyInput, BusinessModel
)
from datetime import datetime
import csv
import io

# Strategies for generating models
def simulation_response_strategy():
    return st.builds(
        SimulationResponse,
        persona_id=st.uuids().map(str),
        decision=st.sampled_from(list(SimulationDecision)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=100),
        # Ensure key factors are not just whitespace and don't become empty after strip()
        key_factors=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=20), 
            min_size=1, max_size=3
        ),
        timestamp=st.just(datetime.utcnow()),
        model_used=st.just("test-model")
    )

def persona_strategy():
    return st.builds(
        SyntheticPersona,
        id=st.uuids().map(str),
        name=st.text(min_size=1, max_size=20),
        demographics=st.builds(
            Demographics,
            age=st.integers(min_value=18, max_value=80),
            role=st.sampled_from(["CEO", "CTO", "Developer", "Manager"]),
            company_size=st.sampled_from(["Startup", "Enterprise", "SMB"]),
            industry=st.just("Tech"),
            income=st.just("High")
        ),
        psychographics=st.builds(
            Psychographics,
            # Added max_size=10 to match Pydantic constraints
            personality_traits=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10),
            values=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10),
            motivations=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10),
            pain_points=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10)
        ),
        behavior_patterns=st.builds(
            BehaviorPatterns,
            technology_adoption=st.sampled_from(list(TechnologyAdoption)),
            decision_making_style=st.text(min_size=1, max_size=50),
            risk_tolerance=st.sampled_from(list(RiskTolerance)),
            information_sources=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10)
        ),
        contextual_factors=st.builds(
            ContextualFactors,
            current_solutions=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
            budget=st.text(min_size=1, max_size=50),
            time_constraints=st.text(min_size=1, max_size=50),
            team_influence=st.text(min_size=1, max_size=50)
        )
    )

class TestPropertyAggregationLayer:
    
    @given(st.lists(simulation_response_strategy(), min_size=1, max_size=50))
    def test_aggregation_calculation(self, results):
        """Property 12: Aggregation calculation accuracy"""
        aggregator = AggregationLayer()
        insights = aggregator.aggregate_results(results)
        
        # Verify adoption rate
        adopt_count = sum(1 for r in results if r.decision == SimulationDecision.ADOPT)
        expected_rate = adopt_count / len(results)
        assert abs(insights.overall_adoption_rate - expected_rate) < 1e-9
        
        # Verify confidence interval bounds
        low, high = insights.confidence_interval
        assert 0.0 <= low <= high <= 1.0

    @given(st.lists(persona_strategy(), min_size=5, max_size=20))
    def test_segmentation_analysis(self, personas):
        """Property 13: Segmentation analysis correctness"""
        # Create corresponding results where everyone adopts
        results = []
        for p in personas:
            results.append(SimulationResponse(
                persona_id=p.id,
                decision=SimulationDecision.ADOPT,
                confidence=0.9,
                reasoning="Test",
                key_factors=["Test"],
                timestamp=datetime.utcnow(),
                model_used="test"
            ))
            
        aggregator = AggregationLayer()
        insights = aggregator.aggregate_results(results, personas)
        
        # Check specific segments
        # 1. Tech Adoption
        tech_adopters = [p for p in personas if p.behavior_patterns.technology_adoption == TechnologyAdoption.EARLY_ADOPTER]
        if tech_adopters:
            key = f"Tech Adoption: {TechnologyAdoption.EARLY_ADOPTER.value}"
            # Since everyone adopted, segment rate should be 1.0
            if key in insights.adoption_by_segment:
                assert insights.adoption_by_segment[key] == 1.0
                
        # 2. Company Size
        startups = [p for p in personas if p.demographics.company_size == "Startup"]
        if startups:
            key = "Company Size: Startup"
            if key in insights.adoption_by_segment:
                assert insights.adoption_by_segment[key] == 1.0

    @given(st.lists(persona_strategy(), min_size=1, max_size=10))
    def test_export_format(self, personas):
        """Property 16: Export format consistency"""
        # Create results
        results = []
        for p in personas:
            results.append(SimulationResponse(
                persona_id=p.id,
                decision=SimulationDecision.ADOPT,
                confidence=0.9,
                reasoning="Test reasoning string",
                key_factors=["Factor1", "Factor2"],
                timestamp=datetime.utcnow(),
                model_used="test"
            ))
            
        # Mock Experiment object (simulated)
        # In a real scenario we'd use a full Experiment strategy, but here we just need
        # an object with .personas and .simulation_results attributes
        class MockExperiment:
            def __init__(self, p, r):
                self.personas = p
                self.simulation_results = r
                
        mock_experiment = MockExperiment(personas, results)
        
        aggregator = AggregationLayer()
        csv_output = aggregator.generate_csv_export(mock_experiment)
        
        # Parse back CSV
        f = io.StringIO(csv_output)
        reader = csv.DictReader(f)
        rows = list(reader)
        
        assert len(rows) == len(personas)
        
        # Check content match for first row
        first_row = rows[0]
        # Find corresponding persona
        # The CSV order depends on the results order which matches generated list
        persona_name = first_row["Persona Name"]
        matching_persona = next((p for p in personas if p.name == persona_name), None)
        assert matching_persona is not None
        
        assert first_row["Reasoning"] == "Test reasoning string"
        assert "Factor1" in first_row["Key Factors"]
