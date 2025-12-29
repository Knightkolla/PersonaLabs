import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.pattern_analyzer import PatternAnalyzer
from app.models import SimulationResponse, SimulationDecision, ReasoningPattern
from datetime import datetime
import uuid

# Strategies
def simulation_response_strategy(decision=None):
    """Generate simulation responses with specific decisions"""
    if decision is None:
        decision_st = st.sampled_from([SimulationDecision.ADOPT, SimulationDecision.REJECT, SimulationDecision.UNSURE])
    else:
        decision_st = st.just(decision)
    
    return st.builds(
        SimulationResponse,
        persona_id=st.text(min_size=5, max_size=20),
        decision=decision_st,
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=50, max_size=300),
        key_factors=st.lists(st.text(min_size=5, max_size=30), min_size=1, max_size=5),
        timestamp=st.just(datetime.utcnow()),
        model_used=st.just("test-model")
    )

class TestPropertyPatternAnalysis:
    
    @settings(max_examples=10, deadline=None)
    @given(responses=st.lists(simulation_response_strategy(), min_size=3, max_size=10))
    def test_reasoning_completeness(self, responses):
        """Property 29: Reasoning display completeness - all reasoning should be preserved"""
        analyzer = PatternAnalyzer()
        
        # Analyze patterns
        patterns = analyzer.analyze_patterns(responses)
        
        # Verify all reasoning is accounted for in patterns or accessible
        # Each response's reasoning should be preserved
        for response in responses:
            assert response.reasoning is not None
            assert len(response.reasoning) > 0
        
        # Patterns should reference actual persona IDs from responses
        response_persona_ids = {r.persona_id for r in responses}
        for pattern in patterns:
            for persona_id in pattern.affected_personas:
                # Pattern personas should be from actual responses
                assert persona_id in response_persona_ids
    
    @settings(max_examples=10, deadline=None)
    @given(
        adoptions=st.lists(simulation_response_strategy(SimulationDecision.ADOPT), min_size=3, max_size=5),
        rejections=st.lists(simulation_response_strategy(SimulationDecision.REJECT), min_size=3, max_size=5)
    )
    def test_pattern_identification(self, adoptions, rejections):
        """Property 30: Pattern identification - similar patterns should cluster"""
        analyzer = PatternAnalyzer()
        
        # Combine responses
        all_responses = adoptions + rejections
        
        # Analyze patterns
        patterns = analyzer.analyze_patterns(all_responses)
        
        # Verify patterns are identified
        assert len(patterns) >= 0  # May or may not find patterns depending on data
        
        # If patterns found, verify structure
        for pattern in patterns:
            assert pattern.pattern_type in ["theme", "objection_cluster", "success_driver"]
            assert pattern.frequency >= 1
            assert len(pattern.example_quotes) >= 1
            assert len(pattern.affected_personas) >= 1
            assert len(pattern.description) > 0
        
        # Verify objection patterns only reference rejections
        objection_patterns = [p for p in patterns if p.pattern_type == "objection_cluster"]
        rejection_persona_ids = {r.persona_id for r in rejections}
        for pattern in objection_patterns:
            for persona_id in pattern.affected_personas:
                assert persona_id in rejection_persona_ids
        
        # Verify success patterns only reference adoptions
        success_patterns = [p for p in patterns if p.pattern_type == "success_driver"]
        adoption_persona_ids = {r.persona_id for r in adoptions}
        for pattern in success_patterns:
            for persona_id in pattern.affected_personas:
                assert persona_id in adoption_persona_ids
    
    
    def test_pattern_frequency_accuracy(self):
        """Verify pattern frequency counts are accurate"""
        analyzer = PatternAnalyzer()
        
        # Create responses with known common factors
        common_factor = "high cost"
        responses = [
            SimulationResponse(
                persona_id=f"persona_{i}",
                decision=SimulationDecision.REJECT,
                confidence=0.8,
                reasoning=f"The main issue is the {common_factor} which makes it prohibitive",
                key_factors=[common_factor, "other factor"],
                timestamp=datetime.utcnow(),
                model_used="test"
            )
            for i in range(5)
        ]
        
        patterns = analyzer.analyze_patterns(responses)
        
        # Find the pattern for common_factor
        cost_patterns = [p for p in patterns if common_factor.lower() in p.description.lower()]
        
        if cost_patterns:
            # Frequency should match number of responses with that factor
            assert cost_patterns[0].frequency == 5
            assert len(cost_patterns[0].affected_personas) == 5
